# Interface Description


### API认证

所有请求过程中,需要在请求的url中添加三个个参数:
- `token`
- `timestamp`
- `sign`

用"&"分隔放于url中, 后台在认证这两点皆为有效后处理请求

`token`: 规定的token

`timestamp`: 发送请求的时的时间戳, 后台规定固定的请求有效时间, 若后台接收到请求的时间在有效时间范围内则认为请求有效

`sign`: 由三部分计算: （请求的资源url + url请求参数 + json数据键值）添加规定的salt串后 md5加密


### API签名
以创建trackings为例, sign分为三部分计算, 一下用python演示:

```json
//url: /trackings?token=xxx&timestamp=1537929616
//request:
{
  "carrier_email": "boris.jing@truckerpath.com",
  "from_date": "2017-09-21T18:31:42Z",
  "to_date": "2017-09-30T18:31:42Z",
  "from_location": {
    "lat": 37.7576793,
    "lng": -122.5076399,
    "address": "San Francisco, CA"
  },
  "to_location": {
    "lat": 34.0201812,
    "lng": -118.691918810,
    "address": "Los Angeles, CA"
  }

}
```

```python
# 第一部分(请求资源的url)
s1 = '/trackings'


# 第二部分(请求参数排序)
# s2 = '?timestamp=1537929616&token=xxx'
re_args = {k: v for k, v in request.args.items()}
if [k + '=' + v for k, v in re_args.items() if k != 'sign']:
    s2 = '?' + reduce(lambda x, y: x + '&' + y, sorted([k + '=' + v for k, v in re_args.items() if k != 'sign'], lambda x, y: cmp(x, y)))
else:
    s2 = ''


# 第三部分(json数据取出键值按照字符序用&分隔)
# s3 = 'carrier_email&from_date&from_location&to_date&to_location'
json_data = copy.deepcopy(request.get_json())
if json_data and len(json_data):
    s3 = reduce(lambda x, y: x + '&' + y, sorted([k for k in json_data.keys()], lambda x, y: cmp(x, y)))
else:
    s3 = ''


# s = '/trackings?timestamp=1537929616&token=xxxcarrier_email&from_date&from_location&to_date&to_location'
s = s1 + s2 + s3


salt = 'hello'
m = hashlib.md5()
m.update(s1)
m.update(salt)
sign = m.hexdigest().upper() #sign = '0C6E5DF1FCFA8A8A5B4E8E9363D245E2'


#最终的请求url为: '/trackings?token=xxx&timestamp=1537929616&sign=0C6E5DF1FCFA8A8A5B4E8E9363D245E2'

```

### <h5 id="resource">资源</h5>
* [1. 获取trackings](#1)
* [2. 创建trackings](#2)
* [3. 获取trackings by id](#3)
* [4. 更新trackings](#4)
* [5. 删除trackings](#5)
* [6. 创建location event](#6)


#### <h5 id="1">1. 获取trackings</h5>
```json
//url: /api/transmit/trackings?broker_id=xxx&token=xxx&timestamp=xxx&sign=xxx
//method: get

//response:
{
    "total": 24,
    "results": [
        {
            "deleted_at": null,
            "from_date": "2018-12-30T14:00:00Z",
            "route": {
                "total": 4442679,
                "covered": 0,
                "remaining": 4442679
            },
            "carrier": {
                "id": 524078,
                "company_name": ""
            },
            "updated_at": "2018-09-18T10:28:51Z",
            "to_location": {
                "lng": -117.68894399999999,
                "lat": 34.0122346,
                "address": "Chino, CA"
            },
            "broker": {
                "id": 524081,
                "company_name": ""
            },
            "status": "pending",
            "shipment_id": null,
            "id": "10996",
            "to_date": "2019-01-03T02:00:00Z",
            "from_location": {
                "lng": -74.0059728,
                "lat": 40.7127753,
                "address": "New York, NY"
            },
            "enabled": false,
            "created_at": "2018-09-18T10:03:11Z"
        },
        {
            "deleted_at": null,
            "from_date": "2018-09-19T01:00:00Z",
            "route": {
                "total": 1126815,
                "covered": null,
                "remaining": null
            },
            "carrier": {
                "id": 525046,
                "company_name": "SCOTT LUMBER COMPANY INC"
            },
            "updated_at": "2018-09-20T11:01:12Z",
            "to_location": {
                "lng": -77.03687070000001,
                "lat": 38.9071923,
                "address": "Washington, DC"
            },
            "broker": {
                "id": 524081,
                "company_name": ""
            },
            "status": "completed",
            "shipment_id": null,
            "id": "10995",
            "to_date": "2018-09-26T01:00:00Z",
            "from_location": {
                "lng": -87.62979819999998,
                "lat": 41.8781136,
                "address": "Chicago, IL"
            },
            "enabled": true,
            "created_at": "2018-09-18T09:11:11Z"
        }
    ]
}
```
[back to resource](#resource)


#### <h5 id="2">2. 创建trackings</h5>
```json
//url: /api/transmit/trackings?timestamp=xxx&token=xxx&sign=xxx
//method: post
//header: 添加 Content-Type: application/json

//request:
{
  "carrier_email": "boris.jing@truckerpath.com",
  "from_date": "2017-09-21T18:31:42Z",
  "to_date": "2017-09-30T18:31:42Z",
  "from_location": {
    "lat": 37.7576793,
    "lng": -122.5076399,
    "address": "San Francisco, CA"
  },
  "to_location": {
    "lat": 34.0201812,
    "lng": -118.691918810,
    "address": "Los Angeles, CA"
  }

}

//response:
{
    "deleted_at": null,
    "tracks": [],
    "from_date": "2017-09-21T18:31:42Z",
    "route": {
        "total": 646142,
        "covered": 0,
        "remaining": 646142,
        "estimated_track": ""
    },
    "carrier": {
        "id": 524081,
        "company_name": "",
        "contact_name": "Borisg Jingf",
        "dot": "6336651",
        "mc": null,
        "email": "boris.jing@truckerpath.com",
        "phone": "1512005291",
        "phone_ext": "000"
    },
    "updated_at": "2018-09-26T04:04:58Z",
    "to_location": {
        "lng": -118.69191881,
        "lat": 34.0201812,
        "address": "Los Angeles, CA"
    },
    "broker": {
        "id": 524081,
        "company_name": ""
    },
    "status": "completed",
    "shipment_id": null,
    "id": "11029",
    "to_date": "2017-09-30T18:31:42Z",
    "from_location": {
        "lng": -122.5076399,
        "lat": 37.7576793,
        "address": "San Francisco, CA"
    },
    "enabled": true,
    "created_at": "2018-09-26T04:04:58Z"
}
```
[back to resource](#resource)


#### <h5 id="3">3. 获取trackings by id</h5>
```json
//url: /api/transmit/trackings/<id>?timestamp=xxx&token=xxx&sign=xxx
//method: get

//response:
{
    "deleted_at": null,
    "tracks": [],
    "from_date": "2017-09-21T18:31:42Z",
    "route": {
        "total": 646142,
        "covered": 0,
        "remaining": 646142,
        "estimated_track": ""
    },
    "carrier": {
        "id": 524081,
        "company_name": "",
        "contact_name": "Borisg Jingf",
        "dot": "6336651",
        "mc": null,
        "email": "boris.jing@truckerpath.com",
        "phone": "1512005291",
        "phone_ext": "000"
    },
    "updated_at": "2018-09-26T04:04:58Z",
    "to_location": {
        "lng": -118.69191881,
        "lat": 34.0201812,
        "address": "Los Angeles, CA"
    },
    "broker": {
        "id": 524081,
        "company_name": ""
    },
    "status": "completed",
    "shipment_id": null,
    "id": "11029",
    "to_date": "2017-09-30T18:31:42Z",
    "from_location": {
        "lng": -122.5076399,
        "lat": 37.7576793,
        "address": "San Francisco, CA"
    },
    "enabled": true,
    "created_at": "2018-09-26T04:04:58Z"
}
```
[back to resource](#resource)


#### <h5 id="4">4. 更新trackings</h5>
```json
//url: /api/transmit/trackings/<id>?timestamp=xxx&token=xxx&sign=xxx
//method: patch
//header: 添加 Content-Type: application/json

//request:
{
  "enabled": false
}

//response:
{
    "deleted_at": null,
    "tracks": [],
    "from_date": "2017-09-21T18:31:42Z",
    "route": {
        "total": 646142,
        "covered": 0,
        "remaining": 646142,
        "estimated_track": ""
    },
    "carrier": {
        "id": 524081,
        "company_name": "",
        "contact_name": "Borisg Jingf",
        "dot": "6336651",
        "mc": null,
        "email": "boris.jing@truckerpath.com",
        "phone": "1512005291",
        "phone_ext": "000"
    },
    "updated_at": "2018-09-26T04:11:30Z",
    "to_location": {
        "lng": -118.69191881,
        "lat": 34.0201812,
        "address": "Los Angeles, CA"
    },
    "broker": {
        "id": 524081,
        "company_name": ""
    },
    "status": "completed",
    "shipment_id": null,
    "id": "11029",
    "to_date": "2017-09-30T18:31:42Z",
    "from_location": {
        "lng": -122.5076399,
        "lat": 37.7576793,
        "address": "San Francisco, CA"
    },
    "enabled": false,
    "created_at": "2018-09-26T04:04:58Z"
}
```
[back to resource](#resource)


#### <h5 id="5">5. 删除trackings</h5>
```json
//url: /api/transmit/trackings/<id>?timestamp=xxx&token=xxx&sign=xxx
//method: delete
```
[back to resource](#resource)


#### <h5 id="6">6. 创建location event</h5>
```json
//url: /api/transmit/location_events?timestamp=xxx&token=xxx&sign=xxx
//method: post
//header: 添加 Content-Type: application/json

//request:
{
  "events": [{
    "id": "1d5d0b30-930d-49bd-9c22-21c93ac0b794",
    "lat": 12.34,
    "lng": 56.78,
    "client_date": "2018-09-21T12:34:56+03:00",
    "location_type": "network"
    }]
}

//response:
{
    "enough": true
}
```
[back to resource](#resource)
