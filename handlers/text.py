# handlers/text.py

from linebot.v3.webhooks import MessageEvent, TextMessageContent, Event
from linebot.v3.messaging import ReplyMessageRequest, TextMessage


def register_text_handler(
    handler,
    messaging_api,
    shopping_service,
    profile_resolver,
    keyword_provider,
):
    print("[DEBUG] register_text_handler CALLED")

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
            # ✅ 1️⃣ 已購買 / 完成（完全外部化）
            # ==================================================
            complete_keywords = keyword_provider.get_keywords(
                conversation_id,
                "complete_keywords",
            )

            matched_kw = None
            matched_idx = None

            for k in complete_keywords:
                idx = text.find(k)
                if idx != -1:
                    matched_kw = k
                    matched_idx = idx
                    break

            if matched_kw is not None:
                item_name = text[matched_idx + len(matched_kw):].strip()

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
            # ✅ 2️⃣ 新增購物項目（完全外部化）
            # ==================================================
            buy_keywords = keyword_provider.get_keywords(
                conversation_id,
                "buy_keywords",
            )

            matched_kw = None
            matched_idx = None

            for k in buy_keywords:
                idx = text.find(k)
                if idx != -1 and (matched_idx is None or idx < matched_idx):
                    matched_kw = k
                    matched_idx = idx

            if matched_kw is not None:
                content = text[matched_idx + len(matched_kw):].strip()

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
            # ✅ 3️⃣ 查詢清單
            # ==================================================
            if text == "清單":
                checklist = shopping_service.get_checklist(conversation_id)

                lines = ["🛒 尚未購買："]
                for item in checklist["pending"]:
                    creator = profile_resolver.get_display_name(
                        user_id=item["created_by"],
                        conversation_id=conversation_id,
                        is_group=is_group,
                    )
                    lines.append(f"- {item['item_name']}（{creator}）")

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


def register_catch_all_handler(handler):
    @handler.add(Event)
    def catch_all(event):
        print("========== CATCH ALL EVENT ==========")
        print(type(event))
        print(event)
        print("=====================================")