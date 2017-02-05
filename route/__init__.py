def response_with_headers(headers, status_code=200):
    """
    Content-Type: text/html
    Set-Cookie: user=gua
    """
    header = 'HTTP/1.1 {} OK\r\n'.format(status_code)
    # for k, v in headers.items():
    #     h = k + ': ' + v + '\r\n'
    #     header += h
    header += ''.join(['{}: {}\r\n'.format(k, v)
                               for k, v in headers.items()])
    return header


def redirect(location, headers=None):
    if headers is None:
        headers = {
            'Content-Type': 'text/html',
        }
    headers['Location'] = location
    header = response_with_headers(headers, 302)
    r = header + '\r\n' + ''
    return r.encode('utf-8')
