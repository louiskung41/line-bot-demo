# handlers/text.py

from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)


def register_text_handler(handler, api, shopping_service):
    print("[DEBUG] register_text_handler CALLED")
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text(event):
        try:
            # ========= 基本資訊 =========
            text = event.message.text.strip()
            user_id = event.source.user_id

            conversation_id = (
                event.source.group_id
                if hasattr(event.source, "group_id")
                else user_id
            )

            print(f"[DEBUG] received text: '{text}'")
            print(f"[DEBUG] conversation_id={conversation_id}, user_id={user_id}")

            # ========= 1️⃣ 新增購物項目 =========
            if "要買" in text or "buy" in text.lower():
                print("[DEBUG] intent = add_items")

                items = shopping_service.add_items(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    text=text,
                )

                print(f"[DEBUG] parsed items = {items}")

                if not items:
                    api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="⚠️ 沒有解析到任何購物項目")
                    )
                    return

                checklist = shopping_service.get_checklist(conversation_id)

                reply_lines = [
                    "✅ 已加入購物清單",
                    "",
                    "🛒 尚未購買：",
                ]

                for item in checklist["pending"]:
                    reply_lines.append(
                        f"- {item['item_name']} ({item['created_by']})"
                    )

                reply_text = "\n".join(reply_lines)
                print("[DEBUG] replying add_items")

                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_text)
                )
                return

            # ========= 2️⃣ 查詢清單 =========
            if "清單" in text:
                print("[DEBUG] intent = list_checklist")

                checklist = shopping_service.get_checklist(conversation_id)

                reply_lines = ["🛒 尚未購買："]

                if checklist["pending"]:
                    for item in checklist["pending"]:
                        reply_lines.append(
                            f"- {item['item_name']} ({item['created_by']})"
                        )
                else:
                    reply_lines.append("（目前沒有項目）")

                if checklist["today_completed"]:
                    reply_lines.append("")
                    reply_lines.append("✅ 今日已完成：")
                    for item in checklist["today_completed"]:
                        reply_lines.append(
                            f"- {item['item_name']}（完成者：{item['completed_by']}）"
                        )

                reply_text = "\n".join(reply_lines)
                print("[DEBUG] replying checklist")

                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_text)
                )
                return

            # ========= 3️⃣ 完成項目 =========
            if text.startswith("已買"):
                print("[DEBUG] intent = complete_item")

                item_name = text.replace("已買", "").strip()
                print(f"[DEBUG] complete item = {item_name}")

                shopping_service.complete_item(
                    conversation_id=conversation_id,
                    item_name=item_name,
                    completed_by=user_id,
                )

                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"✅ 已完成：{item_name}")
                )
                return

            # ========= 4️⃣ 歷史 =========
            if "歷史" in text:
                print("[DEBUG] intent = history")

                history = shopping_service.get_history(conversation_id)

                if not history:
                    api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="📦 最近 7 天沒有購物紀錄")
                    )
                    return

                reply_lines = ["📦 最近 7 天購物紀錄："]
                for item in history:
                    reply_lines.append(
                        f"- {item['item_name']}（完成者：{item['completed_by']}）"
                    )

                api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="\n".join(reply_lines))
                )
                return

            # ========= 5️⃣ 其他訊息（暫時不回） =========
            print("[DEBUG] no matching intent, ignore message")

        except Exception as e:
            # ========= 🔥 關鍵 DEBUG 區 =========
            print("========== HANDLER ERROR ==========")
            print(e)
            print("===================================")

            api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="⚠️ 系統發生錯誤，請稍後再試"
                )
            )


# ✅ Catch‑All Handler：所有沒有被 match 的 event 都會進來
def register_catch_all_handler(handler):
    @handler.add(Event)
    def catch_all(event):
        print("========== CATCH ALL EVENT ==========")
        print("Event type:", type(event))
        print(event)
        print("=====================================")
