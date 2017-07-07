# stego_http
A PoC for hiding and transfering data inside http headers. Very low throughput - suitable for malware C&C communicaton.

The client transforms a message into binary format and encodes it as white spaces inside the request headers. 1s are encoded as a double space and 0s as a single space.

The first space after the colon in the http headers (header: value) is not used to hide data. In case of a double space it's visually very noticable. To retain the hiding capacity of the request a space(or double space) is inserted right before the end of the header (\r\n), which also makes it harder to notice.

Very easy to stop. At it's currnet state the tool is ineffective if the traffic passes through a proxy or security appliance that normalizes the requests, because the space before \r\n will be omitted and there's going to be information loss.

I think it could be made normalization resistant by not inserting a space at the end, but this will lower the throughput even more. Also I'm not sure if normalization will replace double spaces in the middle of the header value with a single space.

In the examples below I used every header that I could think of to maximize the hiding capacity.

Example request with hidden data in it:
```
GET /test/test.php?id=1 HTTP/1.1
accept-encoding: gzip, deflate,  sdch 
x-requested-with: XMLHttpRequest  
accept: text/html, application/xhtml+xml,  application/xml;q=0.9, image/webp, */*;q=0.8 
cache-control: must-revalidate,  public,  max-age=0 
accept-language: bg-BG,  bg;q=0.8, en;q=0.6, de;q=0.7 
user-agent: Mozilla/5.0 (Windows  NT  10.0; Win64;  x64) AppleWebKit/537.36 (KHTML,  like Gecko)  Chrome/58.0.3029.110  Safari/537.36  
referer: http://www.mysite.com/ 
dnt: 1 
upgrade-insecure-requests: 1  
host: 127.0.0.1  
connection: keep-alive 
accept-charset: utf-8, iso-8859-1;q=0.5,  *;q=0.1 


```

The same request without hidden data:
```
GET /test/test.php?id=1 HTTP/1.1
accept-encoding: gzip, deflate, sdch
x-requested-with: XMLHttpRequest
accept: text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, */*;q=0.8
cache-control: must-revalidate, public, max-age=0
accept-language: bg-BG, bg;q=0.8, en;q=0.6, de;q=0.7
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36
referer: http://www.mysite.com/
dnt: 1
upgrade-insecure-requests: 1
host: 127.0.0.1
connection: keep-alive
accept-charset: utf-8, iso-8859-1;q=0.5, *;q=0.1


```

To transfer the message "This is a very secret message!" 7 such requests are sent. (As I said it's very very low throughput)


Some thoughts for future imporovements:
- make the request generation random and don't use fixed headers and values. 
- add an option to make it normalization resistant (if it's possible)
- make the server return a legitimate page. Could also hide data in the page to increase capacity.
- subsequent requests to use links from the returned page (make it as real http traffic as possible)
- make use of POST requests
- make the communication two-way -> server hides data in the responses
