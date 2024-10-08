from flask import Flask, request, Response
import requests
from cachetools import TTLCache

app = Flask(__name__)
cache = TTLCache(maxsize=1000000, ttl=30000)
NEXTDNS_ENDPOINT = "https://dns.nextdns.io/7df33f"
total_requests = 0
cache_misses = 0
cache_hits = 0

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    global total_requests, cache_misses, cache_hits
    total_requests += 1
    if request.method == 'GET' and 'dns' in request.args:
        dns_query = request.args.get('dns')
        cached_response = cache.get(dns_query)
        if cached_response:
            cache_hits += 1
            return Response(cached_response, mimetype='application/dns-message')
        else:
            cache_misses += 1
            response = requests.get(f"{NEXTDNS_ENDPOINT}?dns={dns_query}", headers={'Accept': 'application/dns-message'})
            if response.status_code == 200:
                cache[dns_query] = response.content
                return Response(response.content, mimetype='application/dns-message')
    elif request.method == 'POST' and request.headers.get('Content-Type') == 'application/dns-message':
        dns_query = request.data
        cached_response = cache.get(dns_query)
        if cached_response:
            cache_hits += 1
            return Response(cached_response, mimetype='application/dns-message')
        else:
            cache_misses += 1
            response = requests.post(NEXTDNS_ENDPOINT, headers={'Accept': 'application/dns-message', 'Content-Type': 'application/dns-message'}, data=dns_query)
            if response.status_code == 200:
                cache[dns_query] = response.content
                return Response(response.content, mimetype='application/dns-message')
    elif request.method == 'GET' and request.headers.get('Accept') == 'application/dns-json':
        total_requests += 1
        cache_misses += 1
        response = requests.get(NEXTDNS_ENDPOINT + request.full_path, headers={'Accept': 'application/dns-json'})
        return Response(response.content, mimetype='application/dns-json')
    else:
        return Response("Test custom DoH Gateway Provided by NextDNS", status=444)

@app.route('/stats')
def show_stats():
    stats = f"""
============
Total DNS Request: {total_requests}
Domain Cached: {cache_misses}
Domain Cached Hit: {cache_hits}
============
"""
    return stats

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host="0.0.0.0", port=7860)
