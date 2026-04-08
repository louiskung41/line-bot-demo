# handlers/text.py
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    Event,
)
from linebot.v3.messaging import (
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)


def register_text_handler(handler, messaging_api, shopping_service):
    print("[DEBUG] register_text_handler CALLED (v3)")

    @handler.add(MessageEvent)
    def handle_message(event: MessageEvent):
        try:
            # ===== 只處理文字訊息 =====
            if not isinstance(event.message, TextMessageContent):
                print("[DEBUG] not a TextMessageContent, ignore")
                return

            text = event.message.text.strip()
            user_id = event.source.user_id

            conversation_id = (
                event.source.group_id
                if getattr(event.source, "group_id", None)
                else user_id
            )

            print(f"[DEBUG] received text: '{text}'")
            print(f"[DEBUG] conversation_id={conversation_id}, user_id={user_id}")

            # ===== 1️⃣ 新增購物項目 =====
            if "要買" in text or "buy" in text.lower():
                print("[DEBUG] intent = add_items")

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

                lines = ["✅ 已加入購物清單", "", "🛒 尚未購買："]
                for item in checklist["pending"]:
                    lines.append(f"- {item['item_name']} ({item['created_by']})")

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="\n".join(lines))]
                    )
                )
                return

            # ===== 2️⃣ 查詢清單 =====
            if "清單" in text:
                print("[DEBUG] intent = list_checklist")

                checklist = shopping_service.get_checklist(conversation_id)

                lines = ["🛒 尚未購買："]
                if checklist["pending"]:
                    for item in checklist["pending"]:
                        lines.append(f"- {item['item_name']} ({item['created_by']})")
                else:
                    lines.append("（目前沒有項目）")

                if checklist["today_completed"]:
                    lines.append("")
                    lines.append("✅ 今日已完成：")
                    for item in checklist["today_completed"]:
                        lines.append(
                            f"- {item['item_name']}（完成者：{item['completed_by']}）"
                        )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="\n".join(lines))]
                    )
                )
                return

            # ===== 3️⃣ 完成項目 =====
            if text.startswith("已買"):
                item_name = text.replace("已買", "").strip()
                print(f"[DEBUG] intent = complete_item: {item_name}")

                shopping_service.complete_item(
                    conversation_id=conversation_id,
                    item_name=item_name,
                    completed_by=user_id,
                )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=f"✅ 已完成：{item_name}")]
                    )
                )
                return

            # ===== 4️⃣ 歷史 =====
            if "歷史" in text:
                print("[DEBUG] intent = history")

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
                    lines.append(
                        f"- {item['item_name']}（完成者：{item['completed_by']}）"
                    )

                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="\n".join(lines))]
                    )
                )
                return

            print("[DEBUG] no matching intent")

        except Exception as e:
            print("========== HANDLER ERROR ==========")
            print(e)
            print("===================================")

            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="⚠️ 系統發生錯誤，請稍後再試")]
                )
            )


# ✅ Catch‑All（v3）
def register_catch_all_handler(handler):
    @handler.add(Event)
    def catch_all(event):
        print("========== CATCH ALL EVENT ==========")
        print(type(event))
        print(event)
        print("=====================================")