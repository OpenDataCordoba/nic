SELECT
  d.id,
  d.nombre AS dominio,
  z.nombre AS zona,
  CONCAT(d.nombre, '.', z.nombre) AS full_dominio,
  -- d.estado,
  d.registered,
  d.data_readed,
  d.data_updated,
  d.expire,
  -- por privacidad usamos solo el ID del registrante
  d.registrante_id,
  -- r.name AS registrante_name,
  -- r.legal_uid AS registrante_legal_uid,
  r.created AS registrante_created,
  r.changed AS registrante_changed,
  dns.dns_domain AS first_dns
FROM dominios_dominio d
LEFT JOIN zonas_zona z ON d.zona_id = z.id
LEFT JOIN registrantes_registrante r ON d.registrante_id = r.id
LEFT JOIN LATERAL (
    SELECT dns.dominio AS dns_domain
    FROM dominios_dnsdominio dd
    JOIN dnss_dns dns ON dd.dns_id = dns.id
    WHERE dd.dominio_id = d.id
    ORDER BY dd.orden ASC
    LIMIT 1
) dns ON TRUE
WHERE d.estado = 'no disponible';