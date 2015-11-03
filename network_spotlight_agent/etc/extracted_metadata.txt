from protocols import protocols as p

SUBSCRIBED_METADATAS = [
    p.http.method, p.http.host, p.http.uri,
    p.ftp.filename,
    p.bittorrent.torrent_filename, 
    p.dns.query_name, p.dns.host_addr,
]
