# handlers/text.py

from datetime import datetime
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
    Event,
)
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    PostbackAction,
)

HELP_TEXT = """🛒 購買清單使用方法

➊ 新增購物項目
請用「要買」或你設定的關鍵字開頭，例如：
- 要買 牛奶 衛生紙
- 要買 牛奶, 衛生紙, 垃圾袋

➋ 查看清單
輸入：
清單

➌ 完成項目
- 傳：已買 牛奶
- 或在清單中點 ✅

➍ 清單顯示規則
- 尚未購買
- 今日已完成

➎ 查看歷史
輸入：
歷史
（最近 7 天）
"""


def _fmt_date(date_str: str) -> str:
    """將 ISO datetime 字串轉成 mm/dd"""
    try:
        return datetime.fromisoformat(date_str).strftime("%m/%d")
    except Exception:
        return "--/--"


def register_text_handler(
    handler,
    messaging_api,
    shopping_service,
    profile_resolver,
    keyword_provider,
):
    print("[DEBUG] register_text_handler CALLED")

    # ==================================================
    # ✅ 文字訊息處理
    # ==================================================
    @handler.add(MessageEvent)
    def handle_message(event: MessageEvent):
        try:
            if not isinstance(event.message, TextMessageContent):
                return

            text = event.message.text.strip()
            text_lower = text.lower()
            user_id = event.source.user_id

            is_group = hasattr(event.source, "group_id")
            conversation_id = event.source.group_id if is_group else user_id

            # ==================================================
            # ✅ HELP（help / ? / 完整文字）
            # ==================================================
            if text_lower in ("help", "?") or text == "購買清單使用方法":
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=HELP_TEXT)],
                    )
                )
                return

            # ==================================================
            # ✅ 已購買（文字指令）
            # ==================================================
            complete_keywords = keyword_provider.get_keywords(
                conversation_id, "complete_keywords"
            )
            for k in complete_keywords:
                if text.startswith(k):
                    item_name = text[len(k):].strip()
                    if not item_name:
                        messaging_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(text="⚠️ 請輸入已購買的項目")],
                            )
                        )
                        return

                    shopping_service.complete_item(
                        conversation_id=conversation_id,
                        item_name=item_name,
                        completed_by=user_id,
                    )

                    user_name = profile_resolver.get_display_name(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        is_group=is_group,
                    )
                    today = datetime.now().strftime("%m/%d")

                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                TextMessage(
                                    text=f"✅ {item_name}（{user_name}, {today}）已標記為已購買"
                                )
                            ],
                        )
                    )
                    return

            # ==================================================
            # ✅ 新增購物（要買）
            # ==================================================
            buy_keywords = keyword_provider.get_keywords(
                conversation_id, "buy_keywords"
            )
            for k in buy_keywords:
                if text.startswith(k):
                    content = text[len(k):].strip()
                    if not content:
                        messaging_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[TextMessage(text="⚠️ 請輸入要購買的項目")],
                            )
                        )
                        return

                    shopping_service.add_items(
                        conversation_id=conversation_id,
                        user_id=user_id,
                        text=content,
                    )

                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="✅ 已加入購物清單")],
                        )
                    )
                    return

            # ==================================================
            # ✅ 清單（尚未購買 / 今日已完成）
            # ==================================================
            if text == "清單":
                checklist = shopping_service.get_checklist(conversation_id)

                lines = ["🛒 尚未購買："]
                quick_items = []

                for item in checklist["pending"]:
                    user_name = profile_resolver.get_display_name(
                        user_id=item["created_by"],
                        conversation_id=conversation_id,
                        is_group=is_group,
                    )
                    date = _fmt_date(item.get("created_at"))

                    lines.append(
                        f"- {item['item_name']}（{user_name}, {date}）"
                    )

                    quick_items.append(
                        QuickReplyItem(
                            action=PostbackAction(
                                label=f"✅ {item['item_name']}",
                                data=f"action=complete&item_id={item['item_id']}",
                                display_text=f"已買 {item['item_name']}",
                            )
                        )
                    )

                # 使用說明
                quick_items.append(
                    QuickReplyItem(
                        action=PostbackAction(
                            label="📖 使用說明",
                            data="action=help",
                            display_text="購買清單使用方法",
                        )
                    )
                )

                if checklist["today_completed"]:
                    lines.append("")
                    lines.append("✅ 今日已完成：")
                    for item in checklist["today_completed"]:
                        user_name = profile_resolver.get_display_name(
                            user_id=item["completed_by"],
                            conversation_id=conversation_id,
                            is_group=is_group,
                        )
                        date = _fmt_date(item.get("completed_at"))
                        lines.append(
                            f"- {item['item_name']}（{user_name}, {date}）"
                        )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text="\n".join(lines),
                                quick_reply=QuickReply(items=quick_items),
                            )
                        ],
                    )
                )
                return

            # ==================================================
            # ✅ 歷史
            # ==================================================
            if text == "歷史":
                history = shopping_service.get_history(conversation_id)

                if not history:
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="📦 最近 7 天沒有購物紀錄")],
                        )
                    )
                    return

                lines = ["📦 最近 7 天購物紀錄："]
                for item in history:
                    user_name = profile_resolver.get_display_name(
                        user_id=item["completed_by"],
                        conversation_id=conversation_id,
                        is_group=is_group,
                    )
                    date = _fmt_date(item.get("completed_at"))
                    lines.append(
                        f"- {item['item_name']}（{user_name}, {date}）"
                    )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="\n".join(lines))],
                    )
                )
                return

        except Exception as e:
            print("========== HANDLER ERROR ==========")
            print(e)
            print("===================================")
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="⚠️ 系統錯誤，請稍後再試")],
                )
            )

    # ==================================================
    # ✅ Postback
    # ==================================================
    @handler.add(PostbackEvent)
    def handle_postback(event: PostbackEvent):
        try:
            data = event.postback.data

            if data == "action=help":
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=HELP_TEXT)],
                    )
                )
                return

            params = dict(
                pair.split("=", 1)
                for pair in data.split("&")
                if "=" in pair
            )

            if params.get("action") == "complete":
                item_id = params.get("item_id")
                shopping_service.complete_item_by_id(
                    item_id=item_id,
                    completed_by=event.source.user_id,
                )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="✅ 已標記為已購買")],
                    )
                )

        except Exception as e:
            print("========== POSTBACK ERROR ==========")
            print(e)
            print("===================================")


def register_catch_all_handler(handler):
    @handler.add(Event)
    def catch_all(event):
        print("========== CATCH ALL EVENT ==========")
        print(type(event))
        print(event)
        print("=====================================")