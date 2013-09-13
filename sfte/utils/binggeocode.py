# -*- coding: utf-8 -*-
# see http://msdn.microsoft.com/en-us/library/ff701711.aspx

import json
import urllib

KEY = 'AnxEdZBJLZ-7AwgIyeyoASxnKPpbB70KTqPBAJqZLdN7XzvkwwLkwK5r0otYHTlw'
BASE_URL = 'http://dev.virtualearth.net/REST/v1/Locations'


def _build_url(query):
    params = {
        'key': KEY,
        'query': query,
        'maxResults': 5,
        # http://msdn.microsoft.com/en-us/library/ff701701.aspx
        'suppressStatus': True,
        'output': 'json',
        # http://msdn.microsoft.com/en-us/library/ff701704.aspx
        # San Francisco bounding box. Same values as content/management/commands/find_invalid.py.
        'userMapView': '37.708202,-122.514578,37.810937,-122.357232',
    }

    return BASE_URL + '?' + urllib.urlencode(params)


def _parse_result(json_str):
    results = json.loads(json_str)
    try:
        first_result = results['resourceSets'][0]['resources'][0]
    except IndexError:
        raise GeocodeError('Bing geocode did not return any results for the given address')

    for p in first_result['geocodePoints']:
        if 'Route' in p['usageTypes']:
            break
    else:
        raise GeocodeError('Bing geocode did not return a usable result for the given address')

    return (first_result['address']['addressLine'], (p['coordinates'][1], p['coordinates'][0]))


def query(query):
    url = _build_url(query)
    response = urllib.urlopen(url)
    return _parse_result(response.read())


class GeocodeError(Exception):
    pass


if __name__ == '__main__':
    # TESTS
    # print(_build_url('380 alabama st'))
    # print(_parse_result('{"authenticationResultCode":"ValidCredentials","brandLogoUri":"http:\/\/dev.virtualearth.net\/Branding\/logo_powered_by.png","copyright":"Copyright Â© 2013 Microsoft and its suppliers. All rights reserved. This API cannot be accessed and the content and any results may not be used, reproduced or transmitted in any manner without express written permission from Microsoft Corporation.","resourceSets":[{"estimatedTotal":2,"resources":[{"__type":"Location:http:\/\/schemas.microsoft.com\/search\/local\/ws\/rest\/v1","bbox":[37.760591170368826,-122.41918855163966,37.768316605510179,-122.40615934875034],"name":"380 Alabama St, San Francisco, CA 94110","point":{"type":"Point","coordinates":[37.7644538879395,-122.412673950195]},"address":{"addressLine":"380 Alabama St","adminDistrict":"CA","adminDistrict2":"San Francisco Co.","countryRegion":"United States","formattedAddress":"380 Alabama St, San Francisco, CA 94110","locality":"San Francisco","postalCode":"94110"},"confidence":"High","entityType":"Address","geocodePoints":[{"type":"Point","coordinates":[37.7644538879395,-122.412673950195],"calculationMethod":"Parcel","usageTypes":["Display"]},{"type":"Point","coordinates":[37.7644844055176,-122.412307739258],"calculationMethod":"Interpolation","usageTypes":["Route"]}],"matchCodes":["Good"],"queryParseValues":[{"property":"AddressLine","value":"380 alabama st"}]},{"__type":"Location:http:\/\/schemas.microsoft.com\/search\/local\/ws\/rest\/v1","bbox":[38.105237221894846,-122.26504790745645,38.1129626570362,-122.25195747651191],"name":"380 Alabama St, Vallejo, CA 94590","point":{"type":"Point","coordinates":[38.109099939465523,-122.25850269198418]},"address":{"addressLine":"380 Alabama St","adminDistrict":"CA","adminDistrict2":"Solano Co.","countryRegion":"United States","formattedAddress":"380 Alabama St, Vallejo, CA 94590","locality":"Vallejo","postalCode":"94590"},"confidence":"High","entityType":"Address","geocodePoints":[{"type":"Point","coordinates":[38.109099939465523,-122.25850269198418],"calculationMethod":"InterpolationOffset","usageTypes":["Display"]},{"type":"Point","coordinates":[38.109055012464523,-122.25850336253643],"calculationMethod":"Interpolation","usageTypes":["Route"]}],"matchCodes":["Good"],"queryParseValues":[{"property":"AddressLine","value":"380 alabama st"}]}]}],"statusCode":200,"statusDescription":"OK","traceId":"604a805960894f7bbf0b45110958f7a2|CPKM001257|02.00.161.1800|BY2MSNVM000025, BY2IPEVM000034, BY2MSNVM000061, EWRMSNVM001707"}'))
    # print(query('380 Alabama'))

    # print(query('Chestnut and Fillmore'))

    # print(query('badaddress'))

    pass