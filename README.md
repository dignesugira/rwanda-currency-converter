# Rwanda Currency Converter

Shows what 1 Rwandan franc (RWF) is worth in 160+ currencies, using live rates. Useful for traders, students and families in Rwanda who deal with other currencies, without first converting through USD.

**Live (via load balancer):** https://www.dignesugira.tech
**Demo video:**https://www.loom.com/share/3e6ccedada6e427d95baa2427c05f323
## Features

- Search by currency code (e.g. `KES`)
- Filter to East African currencies
- Sort by code or by rate
- Clear error messages if the API is down or returns an error
- **Bonus:** 10-minute caching of API responses, input validation, XSS-safe templates

## API

[ExchangeRate-API](https://www.exchangerate-api.com/docs/standard-requests), Standard endpoint:


The key is stored in a `.env` file (listed in `.gitignore`), never in the code. It is provided in the submission comment.

## Run locally

```bash
git clone https://github.com/dignesugira/rwanda-currency-converter.git
cd rwanda-currency-converter
pip install flask requests python-dotenv
echo "EXCHANGE_API_KEY=your_key_here" > .env
python app.py
```
Open http://localhost:5000

## Deployment

```
User → lb-01 (HAProxy, HTTPS, round robin) → web-01 / web-02 (Nginx :80 → Gunicorn :5000 → Flask)
```

**On web-01 (18.171.154.145) and web-02 (18.170.86.78):**

```bash
sudo apt update && sudo apt install -y python3-venv nginx git
git clone https://github.com/dignesugira/rwanda-currency-converter.git
cd rwanda-currency-converter
python3 -m venv venv
venv/bin/pip install flask requests python-dotenv gunicorn
nano .env   # EXCHANGE_API_KEY=your_key_here
```

`/etc/systemd/system/currency.service` (keeps the app running and restarts it on boot):
```ini
[Unit]
Description=Rwanda Currency Converter
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/rwanda-currency-converter
ExecStart=/home/ubuntu/rwanda-currency-converter/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload && sudo systemctl enable --now currency
```

`/etc/nginx/sites-available/default` (forwards traffic to Gunicorn and adds a header showing which server answered):
```nginx
server {
    listen 80 default_server;
    server_name _;
    add_header X-Served-By $hostname;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
```bash
sudo nginx -t && sudo systemctl reload nginx
```

**On lb-01 (16.60.29.104)**, HAProxy (`/etc/haproxy/haproxy.cfg`) sends requests to both servers in turn:
```
frontend www_front
    bind *:80
    bind *:443 ssl crt /etc/haproxy/certs/www.dignesugira.tech.pem
    http-request redirect scheme https code 301 unless { ssl_fc }
    default_backend www_back

backend www_back
    balance roundrobin
    server 7409-web-01 18.171.154.145:80 check
    server 7409-web-02 18.170.86.78:80 check
```

**Testing the load balancer:**
```bash
for i in 1 2 3 4; do curl -sI https://www.dignesugira.tech | grep -i served; done
```
```
x-served-by: 7409-web-01
x-served-by: 7409-web-02
x-served-by: 7409-web-01
x-served-by: 7409-web-02
```

**Updating:** on each server, `git pull` then `sudo systemctl restart currency`.

## Challenges

- **`request` vs `requests`:** I mixed up Flask's `request` (reads the user's search) with the `requests` library (calls the API).
- **Wrong base currency:** the page said "1 RWF" but showed USD rates, because the URL still ended in `/USD` from the docs example.
- **Exposed API key:** I pushed a test script with the key in it. I deactivated that key, made a new one, and moved it into `.env`.
- **Empty table:** I looped over `results.items`, but `results` is a list, not a dictionary.
- **web-02 service failing:** `status=200/CHDIR` meant the repo folder didn't exist yet. I had created the service before cloning.

## Credits

[ExchangeRate-API](https://www.exchangerate-api.com) · [Flask](https://flask.palletsprojects.com/) · [Requests](https://requests.readthedocs.io/) · [python-dotenv](https://pypi.org/project/python-dotenv/) · [Gunicorn](https://gunicorn.org/) · [Nginx](https://nginx.org/) · [HAProxy](https://www.haproxy.org/) · [Manrope font](https://fonts.google.com/specimen/Manrope)

**Author:** Digne Sugira ([@dignesugira](https://github.com/dignesugira)), African Leadership University
