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
    keyword_provider,
):
    print("[DEBUG] register_text_handler CALLED (v3 + display name)")

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
            # 新增購物項目
            # ==================================================
            buy_keywords = keyword_provider.get_keywords(conversation_id)
            if any(k in text for k in buy_keywords):
                items = shopping_service.add_items(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    text=text,
                )

                if not items:
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="⚠️ 沒有解析到任何購物項目")]
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
                    lines.append(f"- {item['item_name']}（{creator}）")

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="\n".join(lines))]
                    )
                )
                return

            # ==================================================
            # 查詢清單
            # ==================================================
            if "清單" in text:
                checklist = shopping_service.get_checklist(conversation_id)

                lines = ["🛒 尚未購買："]
                if checklist["pending"]:
                    for item in checklist["pending"]:
                        creator = profile_resolver.get_display_name(
                            user_id=item["created_by"],
                            conversation_id=conversation_id,
                            is_group=is_group,
                        )
                        lines.append(f"- {item['item_name']}（{creator}）")
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
                        messages=[TextMessage(text="\n".join(lines))]
                    )
                )
                return

            # ==================================================
            # 完成項目
            # ==================================================
            if text.startswith("已買"):
                item_name = text.replace("已買", "").strip()

                shopping_service.complete_item(
                    conversation_id=conversation_id,
                    item_name=item_name,
                    completed_by=user_id,
                )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=f"✅ {sender_name} 已完成：{item_name}")]
                    )
                )
                return

            # ==================================================
            # 歷史
            # ==================================================
            if "歷史" in text:
                history = shopping_service.get_history(conversation_id)

                if not history:
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="📦 最近 7 天沒有購物紀錄")]
                        )
                    )
                    return

                lines = ["📦 最近 7 天購物紀錄："]
                for item in history:
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
                        messages=[TextMessage(text="\n".join(lines))]
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
                    messages=[TextMessage(text="⚠️ 系統錯誤，請稍後再試")]
                )
            )


# ==========================================================
# Catch‑All Handler（保險用）
# ==========================================================
def register_catch_all_handler(handler):
    @handler.add(Event)
    def catch_all(event):
        print("========== CATCH ALL EVENT ==========")
        print(type(event))
        print(event)
        print("=====================================")