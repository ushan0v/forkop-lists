# forkop-lists

Встроенные списки [Forkop](https://github.com/ushan0v/forkop): домены и подсети в форматах sing-box и Xray. Собираются раз в сутки из [lists.toml](lists.toml) и [sources](sources).

## Списки

Для Xray: [geosite.dat](https://github.com/ushan0v/forkop-lists/releases/latest/download/geosite.dat), [geoip.dat](https://github.com/ushan0v/forkop-lists/releases/latest/download/geoip.dat).

| Список | Файл | Подсети | Тег .dat |
|---|---|:---:|---|
| RU Blocked (All) | [ru-blocked-all.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-blocked-all.srs) | ✓ | `geosite:ru-blocked-all` `geoip:ru-blocked-all` |
| RU Blocked (RKN) | [ru-blocked-rkn.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-blocked-rkn.srs) | ✓ | `geosite:ru-blocked-rkn` `geoip:ru-blocked-rkn` |
| RU Blocked (Geo) | [ru-blocked-geo.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-blocked-geo.srs) | ✓ | `geosite:ru-blocked-geo` `geoip:ru-blocked-geo` |
| RU Only | [ru-only.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ru-only.srs) |  | `geosite:ru-only` |
| UA Blocked | [ua-blocked.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ua-blocked.srs) |  | `geosite:ua-blocked` |
| AI | [ai.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ai.srs) | ✓ | `geosite:ai` `geoip:ai` |
| ChatGPT | [chatgpt.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/chatgpt.srs) |  | `geosite:chatgpt` |
| Claude | [claude.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/claude.srs) | ✓ | `geosite:claude` `geoip:claude` |
| Cloudflare | [cloudflare.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/cloudflare.srs) | ✓ | `geosite:cloudflare` `geoip:cloudflare` |
| DigitalOcean | [digitalocean.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/digitalocean.srs) | ✓ | `geosite:digitalocean` `geoip:digitalocean` |
| Discord | [discord.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/discord.srs) | ✓ | `geosite:discord` |
| Facebook | [facebook.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/facebook.srs) |  | `geosite:facebook` |
| Gemini | [gemini.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/gemini.srs) |  | `geosite:gemini` |
| GitHub | [github.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/github.srs) |  | `geosite:github` |
| Google Play | [google-play.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/google-play.srs) |  | `geosite:google-play` |
| Hetzner | [hetzner.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/hetzner.srs) | ✓ | `geosite:hetzner` `geoip:hetzner` |
| Instagram | [instagram.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/instagram.srs) |  | `geosite:instagram` |
| OVH | [ovh.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ovh.srs) | ✓ | `geosite:ovh` `geoip:ovh` |
| Roblox | [roblox.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/roblox.srs) | ✓ | `geosite:roblox` `geoip:roblox` |
| Spotify | [spotify.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/spotify.srs) |  | `geosite:spotify` |
| Supercell | [supercell.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/supercell.srs) |  | `geosite:supercell` |
| Telegram | [telegram.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/telegram.srs) | ✓ | `geosite:telegram` `geoip:telegram` |
| TikTok | [tiktok.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/tiktok.srs) |  | `geosite:tiktok` |
| Twitch | [twitch.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/twitch.srs) |  | `geosite:twitch` |
| WhatsApp | [whatsapp.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/whatsapp.srs) | ✓ | `geosite:whatsapp` `geoip:whatsapp` |
| X (Twitter) | [x.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/x.srs) | ✓ | `geosite:x` `geoip:x` |
| YouTube | [youtube.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/youtube.srs) |  | `geosite:youtube` |
| Ads | [ads.srs](https://github.com/ushan0v/forkop-lists/releases/latest/download/ads.srs) |  | `geosite:ads` |


## Предложить правку

- [Добавить в список](https://github.com/ushan0v/forkop-lists/issues/new?template=1-add.yml), если в нём чего то не хватает;
- [Убрать из списка](https://github.com/ushan0v/forkop-lists/issues/new?template=2-remove.yml), если в него попало лишнее;
- [Новый список](https://github.com/ushan0v/forkop-lists/issues/new?template=3-new-list.yml), если считаете, что сервису нужен отдельный список.

## Лицензия

[GPL-3.0](LICENSE)
