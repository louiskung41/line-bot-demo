# handlers/text.py

from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    Event,
)
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
)


def register_text_handler(
    handler,
    messaging_api,
    shopping_service,
    profile_resolver,
    keyword_provider,   # ✅ 關鍵字唯一來源
):
    print("[DEBUG] register_text_handler CALLED")

    @handler.add(MessageEvent)
    def handle_message(event: MessageEvent):
        try:
            # ✅ 只處理文字訊息
            if not isinstance(event.message, TextMessageContent):
                return

            text = event.message.text.strip()
            user_id = event.source.user_id

            is_group = hasattr(event.source, "group_id")
            conversation_id = (
                event.source.group_id if is_group else user_id
            )

            sender_name = profile_resolver.get_display_name(
                user_id=user_id,
                conversation_id=conversation_id,
                is_group=is_group,
            )

            print(f"[DEBUG] received text: '{text}' from {sender_name}")

            # ==================================================
            # ✅ 關鍵字判斷與切除（重點修正在這裡）
            # ==================================================
            buy_keywords = keyword_provider.get_keywords(conversation_id)

            matched_keyword = None
            matched_index = None

            # 找出「最前面出現」的關鍵字
            for k in buy_keywords:
                idx = text.find(k)
                if idx != -1:
                    if matched_index is None or idx < matched_index:
                        matched_keyword = k
                        matched_index = idx

            # ==================================================
            # 新增購物項目
            # ==================================================
            if matched_keyword is not None:
                # ✅ 切掉關鍵字本身
                content = text[
                    matched_index + len(matched_keyword):
                ].strip()

                if not content:
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                TextMessage(text="⚠️ 請輸入要購買的項目")
                            ],
                        )
                    )
                    return

                # ✅ 只把「內容」交給 service / parser
                items = shopping_service.add_items(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    text=content,
                )

                if not items:
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[
                                TextMessage(text="⚠️ 沒有解析到任何購物項目")
                            ],
                        )
                    )
                    return

                checklist = shopping_service.get_checklist(conversation_id)

                lines = [
                    "✅ 已加入購物清單",
                    "",
                    "🛒 尚未購買：",
                ]

                for item in checklist["pending"]:
                    creator = profile_resolver.get_display_name(
                        user_id=item["created_by"],
                        conversation_id=conversation_id,
                        is_group=is_group,
                    )
                    lines.append(
                        f"- {item['item_name']}（{creator}）"
                    )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="\n".join(lines))],
                    )
                )
                return

            # ==================================================
            # 查詢清單
            # ==================================================
            if text == "清單":
                checklist = shopping_service.get_checklist(conversation_id)

                lines = ["🛒 尚未購買："]
                if checklist["pending"]:
                    for item in checklist["pending"]:
                        creator = profile_resolver.get_display_name(
                            user_id=item["created_by"],
                            conversation_id=conversation_id,
                            is_group=is_group,
                        )
                        lines.append(
                            f"- {item['item_name']}（{creator}）"
                        )
                else:
                    lines.append("（目前沒有項目）")

                if checklist["today_completed"]:
                    lines.append("")
                    lines.append("✅ 今日已完成：")
                    for item in checklist["today_completed"]:
                        completer = profile_resolver.get_display_name(
                            user_id=item["completed_by"],
                            conversation_id=conversation_id,
                            is_group=is_group,
                        )
                        lines.append(
                            f"- {item['item_name']}（完成者：{completer}）"
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
# Catch‑all（保險，不影響主流程）
# ==================================================
def register_catch_all_handler(handler):
    @handler.add(Event)
    def catch_all(event):
        print("========== CATCH ALL EVENT ==========")
        print(type(event))
        print(event)
        print("=====================================")