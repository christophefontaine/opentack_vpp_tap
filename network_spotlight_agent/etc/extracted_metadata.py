from network_spotlight_agentd.protocols import protocols as p

SUBSCRIBED_METADATAS = [
    p.http.method, p.http.host, p.http.uri_full, p.http.rtt,
    p.http.server, p.http.user_agent, p.http.request, p.http.request_end,
    p.ftp.filename,
    p.bittorrent.torrent_filename, 
    p.dns.query_name, p.dns.host_addr,
]
