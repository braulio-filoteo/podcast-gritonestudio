# podcast.gritonestudio.com
Sitio estático de GRITones Podcast (146 episodios). Se genera con site_build.py; datos: título, fecha, duración y enlaces a Spotify, Apple Podcasts y YouTube. No incluye textos inventados.

## Episodios nuevos
- `episodes.json` es la fuente de datos; `site_build.py` genera todo el sitio a partir de él.
- `update_episodes.py` lee el feed de Libsyn y añade los episodios que no estén. Corre solo miércoles y jueves (GitHub Actions) y también a mano desde la pestaña Actions → «Actualizar episodios» → Run workflow.
- `hold.json` lista episodios que no se publican aunque estén en el feed (hoy: 142). Quita el número cuando esté aprobado.
- `PENDIENTES.md` se regenera en cada revisión y dice qué enlaces (Spotify, Apple, YouTube) faltan.
- Opcional: para que Spotify se complete solo, crear en GitHub los secretos SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET.
