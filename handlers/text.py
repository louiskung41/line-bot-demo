# handlers/text.py

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
            user_id = event.source.user_id

            is_group = hasattr(event.source, "group_id")
            conversation_id = event.source.group_id if is_group else user_id

            sender_name = profile_resolver.get_display_name(
                user_id=user_id,
                conversation_id=conversation_id,
                is_group=is_group,
            )

            print(f"[DEBUG] received text: '{text}' from {sender_name}")

            # ==================================================
            # ✅ 1️⃣ 已購買（文字指令）
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

                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                TextMessage(
                                    text=f"✅ {item_name} 已標記為已購買（{sender_name}）"
                                )
                            ],
                        )
                    )
                    return

            # ==================================================
            # ✅ 2️⃣ 新增購物（要買）
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
            # ✅ 3️⃣ 查詢清單（含 ✅ checklist）
            # ==================================================
            if text == "清單":
                checklist = shopping_service.get_checklist(conversation_id)

                lines = ["🛒 尚未購買："]
                quick_items = []

                for item in checklist["pending"]:
                    creator = profile_resolver.get_display_name(
                        user_id=item["created_by"],
                        conversation_id=conversation_id,
                        is_group=is_group,
                    )
                    lines.append(f"- {item['item_name']}（{creator}）")

                    # ✅ Checklist ✅（用 item_id）
                    quick_items.append(
                        QuickReplyItem(
                            action=PostbackAction(
                                label=f"✅ {item['item_name']}",
                                data=f"action=complete&item_id={item['item_id']}",
                            )
                        )
                    )

                if checklist["today_completed"]:
                    lines.append("")
                    lines.append("✅ 今日已完成：")
                    for item in checklist["today_completed"]:
                        completer = profile_resolver.get_display_name(
                            user_id=item["completed_by"],
                            conversation_id=conversation_id,
                            is_group=is_group,
                        )
                        lines.append(f"- {item['item_name']}（完成者：{completer}）")

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text="\n".join(lines),
                                quick_reply=QuickReply(items=quick_items)
                                if quick_items
                                else None,
                            )
                        ],
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
    # ✅ Checklist 打勾（PostbackEvent）
    # ==================================================
    @handler.add(PostbackEvent)
    def handle_postback(event: PostbackEvent):
        try:
            data = event.postback.data
            params = dict(
                pair.split("=", 1)
                for pair in data.split("&")
                if "=" in pair
            )

            if params.get("action") == "complete":
                item_id = params.get("item_id")
                user_id = event.source.user_id

                shopping_service.complete_item_by_id(
                    item_id=item_id,
                    completed_by=user_id,
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

    # ==================================================
    # Catch‑all
    # ==================================================
    @handler.add(Event)
    def catch_all(event):
        print("========== CATCH ALL EVENT ==========")
        print(type(event))
        print(event)
        print("=====================================")