# forkop-lists

Встроенные списки [Forkop](https://github.com/ushan0v/forkop): домены и подсети в формате sing-box. Собираются раз в сутки из [lists.toml](lists.toml).

## Регионы

| Список | Файл | Размер | Что внутри |
|---|---|---:|---|
| RU Blocked (All) | [ru-blocked-all.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-blocked-all.srs) | 490 КБ | всё, что заблокировано в России (RKN + Geo) |
| RU Blocked (RKN) | [ru-blocked-rkn.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-blocked-rkn.srs) | 480 КБ | то, что блокирует или замедляет РКН |
| RU Blocked (Geo) | [ru-blocked-geo.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-blocked-geo.srs) | 9 КБ | сервисы, которые сами закрыли доступ из России |
| RU Only | [ru-only.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-only.srs) | 5 КБ | российские сервисы, которые не работают через VPN |
| UA Blocked | [ua-blocked.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ua-blocked.srs) | 9 КБ | сайты, заблокированные в Украине |

## Сервисы

| Список | Файл | Размер | Подсети |
|---|---|---:|:---:|
| AI | [ai.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ai.srs) | 2 КБ | ✓ |
| ChatGPT | [chatgpt.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/chatgpt.srs) | 0,4 КБ | |
| Claude | [claude.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/claude.srs) | 0,3 КБ | ✓ |
| Cloudflare | [cloudflare.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/cloudflare.srs) | 0,3 КБ | ✓ |
| Discord | [discord.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/discord.srs) | 0,6 КБ | ✓ |
| Facebook | [facebook.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/facebook.srs) | 3 КБ | |
| Gemini | [gemini.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/gemini.srs) | 0,5 КБ | |
| GitHub | [github.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/github.srs) | 0,7 КБ | |
| Google Play | [google-play.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/google-play.srs) | 0,3 КБ | |
| Instagram | [instagram.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/instagram.srs) | 0,7 КБ | |
| Roblox | [roblox.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/roblox.srs) | 0,6 КБ | ✓ |
| Spotify | [spotify.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/spotify.srs) | 0,4 КБ | |
| Supercell | [supercell.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/supercell.srs) | 0,3 КБ | |
| Telegram | [telegram.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/telegram.srs) | 0,4 КБ | ✓ |
| TikTok | [tiktok.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/tiktok.srs) | 0,5 КБ | |
| Twitch | [twitch.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/twitch.srs) | 0,4 КБ | |
| WhatsApp | [whatsapp.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/whatsapp.srs) | 0,7 КБ | ✓ |
| X (Twitter) | [x.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/x.srs) | 0,5 КБ | ✓ |
| YouTube | [youtube.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/youtube.srs) | 1,2 КБ | |
| Ads | [ads.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ads.srs) | 1,6 МБ | |

## Предложить правку

Откройте issue по шаблону:

- [Добавить в список](https://github.com/ushan0v/forkop-lists/issues/new?template=1-add.yml), если в нём не хватает сайта или адреса;
- [Убрать из списка](https://github.com/ushan0v/forkop-lists/issues/new?template=2-remove.yml), если в него попало лишнее и из-за этого что-то не работает;
- [Предложить новый список](https://github.com/ushan0v/forkop-lists/issues/new?template=3-new-list.yml), если сервису нужен свой путь или свои подсети.

## Лицензия

[GPL-3.0](LICENSE)
