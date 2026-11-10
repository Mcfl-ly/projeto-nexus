-- Execute no PostgreSQL antes de liberar a rota atualizada.
-- Se houver duplicados, a transacao falha sem apagar registros.
-- Revise os grupos com as consultas abaixo e resolva-os antes de repetir.
-- SELECT user_id, content_type, external_api_id, array_agg(id ORDER BY id)
-- FROM userlibrary WHERE external_api_id IS NOT NULL
-- GROUP BY user_id, content_type, external_api_id HAVING count(*) > 1;
-- SELECT user_id, content_id, array_agg(id ORDER BY id)
-- FROM userlibrary GROUP BY user_id, content_id HAVING count(*) > 1;
-- SELECT user_id, content_type, lower(btrim(name)), array_agg(id ORDER BY id)
-- FROM userlibrary WHERE external_api_id IS NULL
-- GROUP BY user_id, content_type, lower(btrim(name)) HAVING count(*) > 1;
BEGIN;
CREATE UNIQUE INDEX IF NOT EXISTS userlibrary_user_content_unique
    ON userlibrary (user_id, content_id);
CREATE UNIQUE INDEX IF NOT EXISTS userlibrary_user_external_unique
    ON userlibrary (user_id, content_type, external_api_id)
    WHERE external_api_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS userlibrary_user_manual_title_unique
    ON userlibrary (user_id, content_type, lower(btrim(name)))
    WHERE external_api_id IS NULL;
COMMIT;
