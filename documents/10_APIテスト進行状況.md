# APIテスト進行状況レポート

**注意**: このレポートはAPIの単体テストが完了するたびに更新されます。テスト完了後は必ず最新の状況を反映させてください。

**最終更新日**: 2025年3月21日

## 1. 認証・ユーザー関連API

| API ID | エンドポイント | メソッド | テスト状況 | 備考 |
|--------|--------------|---------|----------|------|
| AUTH-001 | `/api/v1/auth/register` | POST | ✅ 完了 | 正常に動作 |
| AUTH-002 | `/api/v1/auth/login` | POST | ✅ 完了 | 正常に動作 |
| AUTH-003 | `/api/v1/auth/logout` | POST | ✅ 完了 | 正常に動作（Authorizationヘッダーが必要） |
| AUTH-004 | `/api/v1/auth/refresh` | POST | ✅ 完了 | 修正済み・正常に動作 |
| AUTH-005 | `/api/v1/auth/password/reset` | POST | ✅ 完了 | 正常に動作（実際にはメール送信されない） |
| AUTH-006 | `/api/v1/auth/password/confirm` | POST | ✅ 完了 | 正常に動作（フィールド名は`new_password`） |
| AUTH-007 | `/api/v1/auth/email/verify` | GET | ✅ 完了 | 正常に動作 |
| USR-001 | `/api/v1/users/me` | GET | ✅ 完了 | 正常に動作 |
| USR-002 | `/api/v1/users/me` | PATCH | ❌ 未テスト | - |
| USR-003 | `/api/v1/users/password` | PUT | ❌ 未テスト | - |
| USR-004 | `/api/v1/users/me` | DELETE | ❌ 未テスト | - |

## 2. 発言フィード関連API

| API ID | エンドポイント | メソッド | テスト状況 | 備考 |
|--------|--------------|---------|----------|------|
| STMT-001 | `/api/v1/statements` | GET | ✅ 完了 | 正常に動作 |
| STMT-002 | `/api/v1/statements/following` | GET | ✅ 完了 | 正常に動作（データなし） |
| STMT-003 | `/api/v1/statements/{statement_id}` | GET | ✅ 完了 | 修正済み・正常に動作 |
| STMT-004 | `/api/v1/statements/politicians/{politician_id}` | GET | ✅ 完了 | 正常に動作（パスが仕様書と異なる） |
| STMT-005 | `/api/v1/statements/parties/{party_id}` | GET | ✅ 完了 | 正常に動作（パスが仕様書と異なる） |
| STMT-006 | `/api/v1/statements/topics/{topic_id}` | GET | ✅ 完了 | 正常に動作（パスが仕様書と異なる） |
| STMT-007 | `/api/v1/search/statements` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| INT-001 | `/api/v1/statements/{statement_id}/like` | POST | ✅ 完了 | 正常に動作 |
| INT-002 | `/api/v1/statements/{statement_id}/like` | DELETE | ✅ 完了 | 正常に動作 |
| INT-003 | `/api/v1/comments/statement/{statement_id}` | POST | ✅ 完了 | 正常に動作 |
| INT-004 | `/api/v1/comments/statement/{statement_id}` | GET | ✅ 完了 | 正常に動作 |
| INT-005 | `/api/v1/comments/{comment_id}` | PUT | ✅ 完了 | 正常に動作 |
| INT-006 | `/api/v1/comments/{comment_id}` | DELETE | ✅ 完了 | 正常に動作 |
| INT-007 | `/api/v1/comments/{comment_id}/replies` | GET | ✅ 完了 | 正常に動作（データなし） |
| INT-008 | `/api/v1/comments/{comment_id}/like` | POST | ✅ 完了 | 正常に動作 |
| INT-009 | `/api/v1/comments/{comment_id}/like` | DELETE | ✅ 完了 | 正常に動作 |
| INT-010 | `/api/v1/comments/{comment_id}/report` | POST | ✅ 完了 | 正常に動作（クエリパラメータとして`reason`を渡す必要あり） |

## 3. 政治家・政党関連API

| API ID | エンドポイント | メソッド | テスト状況 | 備考 |
|--------|--------------|---------|----------|------|
| POL-001 | `/api/v1/politicians` | GET | ✅ 完了 | 正常に動作 |
| POL-002 | `/api/v1/politicians/{politician_id}` | GET | ✅ 完了 | 修正済み・正常に動作 |
| POL-003 | `/api/v1/politicians/{politician_id}/follow` | POST | ✅ 完了 | 正常に動作 |
| POL-004 | `/api/v1/politicians/{politician_id}/follow` | DELETE | ✅ 完了 | 正常に動作 |
| POL-005 | `/api/v1/politicians/{politician_id}/topics` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| PTY-001 | `/api/v1/parties` | GET | ✅ 完了 | 正常に動作 |
| PTY-002 | `/api/v1/parties/{party_id}` | GET | ✅ 完了 | 正常に動作 |
| PTY-003 | `/api/v1/parties/{party_id}/politicians` | GET | ⚠️ 問題あり | レスポンスモデルが`List[PartySchema]`になっており、政治家ではなく政党のデータが返される |
| PTY-004 | `/api/v1/parties/{party_id}/topics` | GET | ❌ 未実装 | エンドポイントが実装されていない |

## 4. 政策トピック関連API

| API ID | エンドポイント | メソッド | テスト状況 | 備考 |
|--------|--------------|---------|----------|------|
| TOP-001 | `/api/v1/topics` | GET | ✅ 完了 | 正常に動作 |
| TOP-002 | `/api/v1/topics/{topic_id}` | GET | ✅ 完了 | 正常に動作 |
| TOP-003 | `/api/v1/topics/{topic_id}/follow` | POST | ✅ 完了 | 正常に動作 |
| TOP-004 | `/api/v1/topics/{topic_id}/follow` | DELETE | ✅ 完了 | 正常に動作 |
| TOP-005 | `/api/v1/topics/{topic_id}/parties` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| TOP-006 | `/api/v1/topics/trending` | GET | ❌ 実装に問題あり | エンドポイントのパスが`/{id}`と競合している可能性あり |

## 5. マイページ関連API

| API ID | エンドポイント | メソッド | テスト状況 | 備考 |
|--------|--------------|---------|----------|------|
| ACT-001 | `/api/v1/users/me/following/politicians` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-002 | `/api/v1/users/me/following/topics` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-003 | `/api/v1/users/me/likes` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-004 | `/api/v1/users/me/comments` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-005 | `/api/v1/users/me/history` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-006 | `/api/v1/users/me/feed` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-007 | `/api/v1/users/me/notifications` | GET | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-008 | `/api/v1/users/me/notifications/{notification_id}/read` | POST | ❌ 未実装 | エンドポイントが実装されていない |
| ACT-009 | `/api/v1/users/me/notifications/read-all` | POST | ❌ 未実装 | エンドポイントが実装されていない |

## 修正した問題点

1. **リフレッシュトークンAPI (AUTH-004)の問題**:
   - 問題: トークンのペイロードから取得した`sub`フィールドをメールアドレスとして扱っていたが、実際には`sub`フィールドにはユーザーIDが格納されていた
   - 修正: `get_user_by_email(db, email=token_data.sub)`を`get_user(db, id=token_data.sub)`に変更し、`get_user`関数をインポート

2. **発言詳細API (STMT-003)の問題**:
   - 問題1: `get_statement_topics`関数でスキーマとモデルの名前が同じことによる混同
   - 修正1: モデルを明示的に指定するために`StatementTopic as StatementTopicModel`としてインポート
   
   - 問題2: `Statement`スキーマで`politician_name`フィールドが必須だが、設定されていなかった
   - 修正2: `politician_name`フィールドをオプションに変更し、`read_statement`関数内で明示的に設定するよう修正

3. **政治家詳細情報取得API (POL-002)の問題**:
   - 問題: `PoliticianWithDetails.model_validate(politician)`でモデルをスキーマに変換する際に型の不一致が発生
   - 修正: モデルを辞書に変換してからスキーマに変換するように修正
   ```python
   # 修正前
   result = PoliticianWithDetails.model_validate(politician)
   
   # 修正後
   politician_dict = {
       "id": politician.id,
       "name": politician.name,
       # その他の属性...
   }
   result = PoliticianWithDetails.model_validate(politician_dict)
   ```

## テスト進行状況の概要

- **完了**: 32 API
- **未テスト**: 20 API
- **未実装**: 3 API
- **合計**: 55 API
- **進捗率**: 約58.2%

## 次のステップ

1. 残りのAPIのテストを継続
2. トピック関連の残りのAPI（TOP-005, TOP-006）のテスト
3. マイページ関連API（ACT-001〜ACT-009）の実装と確認
4. 実装が必要なAPI（POL-005, PTY-004, STMT-007）の実装
5. 修正が必要なAPI（PTY-003）の修正
5. 認証関連の残りのAPI（AUTH-003, AUTH-005〜AUTH-007）のテスト