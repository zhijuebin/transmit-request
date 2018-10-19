# Freight Tracking

## URL composition

URL consists of four parts: request resource, timestamp, accessKey, signature.

- `resource`
- `timestamp`
- `accessKey`
- `signature`

`resource`: the resources you requested.

`timestamp`: it is the timestamp of the UTC time when the request is sent. Its unit is seconds.

`accessKey`: for each user, the agreed accessKey.

`signature`: API signature using SHA1 encryption algorithm


### Signature
The background first processes the requested resources, parameters and body data in a certain order to get a string for encryption, then uses the SHA1 algorithm to encrypt, and finally gets the API signature

The string used for encryption consists of three parts.

- `resource link`: the resource requested with the ordered parameters. These parameters are sorted according to the initial alphabet of the key to form an ordered key value pair.
- `body data`: When post/patch data, JSON format data will be sent. If the request method are get/delete, the body data is an empty string.
- `secretKey`: for each user, there's an agreed secret key.

The string used for encryption: S = resource link + body data + secretKey

signature = upperCase(SHA1(S))

```
Example 1:
----------
Method: GET
URL:host + url_prefix + /trackings?broker_id=524081&accessKey=xxx&timestamp=1539757950

Step1: Ordered parameters:
       S1 = '/trackings?accessKey=xxx&broker_id=524081&timestamp=1539757950'

Step2: no body data
       S2 = ''

Step3: secretKey=test
       S3 = 'test'

The string used for encryption:
       S = (S1 + S2 + S3).encode('utf-8')

       signature = upperCase(sha1(S)) = 'D98EFC7F313C977DAF8EC24591CA0ECD70AE964D'


Example2:
---------
Method: POST
URL:host + url_prefix + /trackings?timestamp=1539690390&accessKey=xxx

Step1: Ordered parameters
       S1 = '/trackings?accessKey=xxx&timestamp=1539690390'

Step2: body data
       S2 = '{\n  "carrier_email": "boris.jing@truckerpath.com",\n  "from_date": "2017-09-21T18:31:42Z",\n  "to_date": "2017-09-30T18:31:42Z",\n  "from_location": {\n    "lat": 37.7576793,\n    "lng": -122.5076399,\n    "address": "San Francisco, CA" \n  },\n  "to_location": {\n    "lat": 34.0201812,\n    "lng": -118.691918810,\n    "address": "Los Angeles, CA"\n  }\n  \n}'

Step3: secretKey=test
       S3 = 'test'

The string used for encryption:
       S = (S1 + S2 + S3).encode('utf-8')

       signature = upperCase(sha1(S)) = 'B50677D187FD406B3CCA337BEF6B5F97686AE1B4'
```


## Returns a list of trackings which belongs to a specific user

### Request

```bash
curl -X GET /trackings?timestamp=xxx&accessKey=xxx&signature=xxx
curl -X GET /trackings?carrier_id=12345&timestamp=xxx&accessKey=xxx&signature=xxx
```

Client should request one of the above, in case of both specified, reply with 400.
In case of unknown broker or carrier id reply with 404.
In case of current user's id is neither broker_id nor carrier_id reply with 403.
Carrier's & broker's company names are taken from saferwatch, in case of saferwatch failure it's empty string.

From and to location in the response should be represented as a geopoint + geocoded address.

No paging required for the first version.

Tracking status should be one of the following:
- `pending`
- `active`
- `completed`
- `canceled`

`pending`: the tracking is created and scheduled, however there are no tracking events _after_ the
`from_date` field.

`active`: the tracking has started and there are locations after `from_date` period and the current time is before `to_date`.

`completed`: the tracking has finished, the current time is after `to_date` field.

`canceled`: is reserved for canceling the tracking either from the client or by a broker. Not supported in the first version.

### Response

```json
{
  "total": 1,
  "results": [{
    "id": "143700",
    "created_at": "2017-04-30T12:34:56Z",
    "updated_at": "2017-04-30T12:34:56Z",
    "deleted_at": null,
    "from_date": "2017-05-30T12:34:56Z",
    "to_date": "2017-08-30T12:34:56Z",
    "enabled": true,
    "from_location": {
      "lat": 37.7576793,
      "lng": -122.5076399,
      "address": "San Francisco, CA"
    },
    "to_location": {
      "lat": 34.0201812,
      "lng": -118.691918810,
      "address": "Los Angeles, CA"
    },
    "status": "pending|active|completed",
    "carrier": {
      "id": 4234,
      "company_name": "B&M SERVICES"
    },
    "broker": {
      "id": 95106,
      "company_name": "OUILLET FARMS"
    },
    "route": {
      "covered": 100,
      "remaining": 900,
      "total": 1000
    }
  }]
}
```

#### Url params

One of the parameters is mandatory.

| Param         | Type        | Restrictions    | Description                                         |
|---------------|-------------|-----------------|-----------------------------------------------------|
| broker_id     | String      | Optional        | If specified, return a list of broker's trackings   |
| carrier_id    | String      | Optional        | If specified, return a list of carrier's trackings  |

#### Response params

| Param                  | Type             | Key mandatory?       | Nullable?               |
|------------------------|------------------|----------------------|-------------------------|
| id                     | String           | Yes                  | No                      |
| created_at             | String           | Yes                  | No                      |
| updated_at             | String           | Yes                  | No                      |
| deleted_at             | String           | Yes                  | Yes                     |
| from_date              | String           | Yes                  | No                      |
| to_date                | String           | Yes                  | No                      |
| enabled                | Boolean          | Yes                  | No                      |
| from_location          | Location         | Yes                  | No                      |
| to_location            | Location         | Yes                  | No                      |
| carrier.id             | Int              | Yes                  | No                      |
| carrier.company_name   | String           | Yes                  | No                      |
| broker.id              | Int              | Yes                  | No                      |
| broker.company_name    | String           | Yes                  | No                      |
| status                 | String           | Yes                  | No                      |
| route.covered          | Number           | Yes                  | Yes                     |
| route.remaining        | Number           | Yes                  | Yes                     |
| route.total            | Number           | Yes                  | Yes                     |


## Saves a new Tracking to the system

### Request

```bash
curl -X POST /trackings?timestamp=xxx&accessKey=xxx&signature=xxx -H "Content-Type: application/json"
```

Duplicate trackings for the same carrier are not allowed at the moment.
When `carrier_email` is supplied, endpoint tries to find a user with supplied email.
If such user exists, creates new tracking. If no user is found, sends an email to
`freighttracking-onboarding+carriers@truckerpath.com` with mandrill template
`freighttracking-onboarding-request` and responds with `202`.
When both `carrier_id` and `carrier_email` are provided, responds with `400`.
The endpoint will reply with 409 in case of existence of non-completed tracking for specified `carrier_id`.
Carrier's & broker's company names are taken from saferwatch, in case of saferwatch failure it's empty string.
When `shipment_id` is supplied, endpoint tries to find not deleted shipment with specified id and then saves this id in the tracking entry.
Id of created tracking is saved to the `trackings` column of specified shipment.

```json

{
  "carrier_email": "boris.jing@truckerpath.com",
  "from_date": "2017-08-09T18:31:42Z",
  "to_date": "2017-09-09T18:31:42Z",
  "from_location": {
    "lat": 37.7576793,
    "lng": -122.5076399,
    "address": "San Francisco, CA"
  },
  "to_location": {
    "lat": 34.0201812,
    "lng": -118.691918810,
    "address": "Los Angeles, CA"
  },
  "shipment_id": 1
}
```


#### Body params

| Param            | Type             | Restrictions                        | Description             |
|------------------|------------------|-------------------------------------|-------------------------|
| from_date        | String           | Required                            |                         |
| to_date          | String           | Required                            |                         |
| from_location    | Location         | Optional                            |                         |
| to_location      | Location         | Optional                            |                         |
| carrier_id       | Int              | Required, if carrier_email absent   |                         |
| carrier_email    | String, email    | Required, if carrier_id absent      |                         |
| broker_id        | Int              | Required                            |                         |
| shipment_id      | Int              | Optional                            |                         |



## Returns a single tracking by id

### Request

```bash
curl -X GET /trackings/123?timestamp=xxx&accessKey=xxx&signature=xxx
```

// return 404 if not available

### Response

```json
{
  "id": "string",
  "created_at": "string",
  "updated_at": "string",
  "deleted_at": "string",
  "from_date": "string",
  "to_date": "string",
  "from_location": Location,
  "to_location": Location,
  "status": "pending|active|completed",
  "enabled": true,
  "carrier": {
    "id": "4234",
    "company_name": "B&M SERVICES",
    "contact_name": "Ivan Petrov",
    "dot": "123456",
    "mc": "998877",
    "email": "ivan.petrov@truckerpath.com",
    "phone": "99824777777",
    "phone_ext": "001"
  },
  "broker": {
    "id": "2345",
    "company_name": "B Brokers"
  },
  "tracks": [{
    "id": "some_persistent_random_id",
    "events": [{
      "id": "string",
      "client_date": "string",
      "location": Location,
      "type": "string"
  }]}],
  "route": {
    "covered": 100, // distance between pickup location and last tracked location
    "remaining": 900, // total - covered
    "total": 1000, // calculated distance between start and end location in Tracking
    "estimated_track": "polyline-encoded string" // see https://developers.google.com/maps/documentation/utilities/polylinealgorithm
  }
}
```

Array of events is sorted by timestamp ascending.
`estimated_track` for finished trackings will be equal to `""`.
When something internal errors occured it will equal to `""` as well.


#### Response params

| Param                  | Type                  | Key mandatory?       | Nullable?               |
|------------------------|-----------------------|----------------------|-------------------------|
| id                     | String                | Yes                  | No                      |
| created_at             | String                | Yes                  | No                      |
| updated_at             | String                | Yes                  | No                      |
| deleted_at             | String                | Yes                  | Yes                     |
| from_date              | String                | Yes                  | No                      |
| to_date                | String                | Yes                  | No                      |
| from_location          | Location              | Yes                  | No                      |
| to_location            | Location              | Yes                  | No                      |
| carrier.id             | String                | Yes                  | No                      |
| carrier.company_name   | String                | Yes                  | No                      |
| carrier.contact_name   | String                | Yes                  | Yes                     |
| carrier.mc             | String                | Yes                  | Yes                     |
| carrier.dot            | String                | Yes                  | Yes                     |
| carrier.email          | String                | Yes                  | Yes                     |
| carrier.phone          | String                | Yes                  | Yes                     |
| carrier.phone_ext      | String                | Yes                  | Yes                     |
| broker.id              | String                | Yes                  | No                      |
| broker.company_name    | String                | Yes                  | No                      |
| events                 | Array[TrackingEvent]  | Yes                  | No                      |
| status                 | String                | Yes                  | No                      |
| route|covered          | Number                | Yes                  | No                      |
| route|remaining        | Number                | Yes                  | No                      |
| route|total            | Number                | Yes                  | No                      |
| route|estimated_track  | String                | Yes                  | No                      |
| enabled                | Boolean               | Yes                  | No                      |



## Edit tracking by id

### Request

```bash
curl -X PATCH /trackings/123?timestamp=xxx&accessKey=xxx&signature=xxx -H "Content-Type:application/json"
```

```json
{
  "enabled": true
}
```

### Body params

| Param            | Type             | Restrictions                        | Description                           |
|------------------|------------------|-------------------------------------|---------------------------------------|
| enabled          | Boolean          | Required                            | If tracking allowed from carrier side |

### Response

```
status codes:
200 - Success
400 - Error in body
403 - Auth error
404 - Tracking not found
```

```json
{
  "id": "string",
  "created_at": "string",
  "updated_at": "string",
  "deleted_at": "string",
  "from_date": "string",
  "to_date": "string",
  "from_location": Location,
  "to_location": Location,
  "status": "pending|active|completed",
  "enabled": true,
  "carrier": {
    "id": "4234",
    "company_name": "B&M SERVICES",
    "contact_name": "Ivan Petrov",
    "dot": "123456",
    "mc": "998877",
    "email": "ivan.petrov@truckerpath.com",
    "phone": "99824777777",
    "phone_ext": "001"
  },
  "broker": {
    "id": "2345",
    "company_name": "B Brokers"
  },
  "tracks": [{
    "id": "some_persistent_random_id",
    "events": [{
      "id": "string",
      "client_date": "string",
      "location": Location,
      "type": "string"
  }]}],
  "route": {
    "covered": 100, // distance between pickup location and last tracked location
    "remaining": 900, // total - covered
    "total": 1000, // calculated distance between start and end location in Tracking
    "estimated_track": "polyline-encoded string" // see https://developers.google.com/maps/documentation/utilities/polylinealgorithm
  }
}
```


## Delete tracking by id

### Request

```bash
curl -X DELETE /trackings/123?timestamp=xxx&accessKey=xxx&signature=xxx
```

### Response

```
status codes:
204 - Success
404 - Tracking not found
```

## Add tracking events

### Request

```bash
curl -X POST /location_events?timestamp=xxx&accessKey=xxx&signature=xxx
```

Since clients will retrieve location more often than send, they need an ability to send multiple events at time.
It also can be useful if user doesn't have internet connection while still receives location updates.
Batch size is limited to 1000 events, if client has more than 1000 events it should send them in separate batches.

```json
{
  "events": [{
    "id": "UUID",
    "lat": 12.34,
    "lng": 56.78,
    "client_date": "2017-04-30T12:34:56+03:00",
    "location_type": "network|gps|fused|unknown"
    }]
}
```

### Body params
| Param            | Type             | Restrictions                        | Description             |
|------------------|------------------|-------------------------------------|-------------------------|
| id               | UUID             | Required                            |                         |
| lat              | Number           | Required                            |                         |
| lng              | Number           | Required                            |                         |
| location_type    | Enum[String]     | Required                            |                         |
| client_date      | String           | Required                            | ISO-8601 with origin's time zone |


### Response
```
status codes:
200 - Success
400 - Error in body
403 - Auth error
```
### Response body (in case of success):

```json
{
  "enough": true|false
}
```

