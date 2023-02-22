const https = require('https');
var responseBody = {"Message": "If you see this then the API call did not work"};
const doGetRequest = () => {

  return new Promise((resolve, reject) => {
    const options = { 
      host: 'stackoverflow.com',
      path: '/questions/66376601/aws-api-gateway-with-lambda-http-get-request-node-js-502-bad-gateway',
      method: 'GET'
    };
    var body='';
    //create the request object with the callback with the result
    const req = https.request(options, (res) => {

      res.on('data', function (chunk) {
            body += chunk;
        });
      res.on('end', function () {
         console.log("Result", body.toString());
         resolve(body);
      });
      
    });

    // handle the possible errors
    req.on('error', (e) => {
      reject(e.message);
    });
    //finish the request
    req.end();
  });
};

exports.handler =   (event, context, callback) => {
    console.log('event',event, 'context',context);
    

    doGetRequest().then(result => {
    var response = {
        "statusCode": 200,
        "headers": {
            "my_header": "my_value"
        },
        "body": JSON.stringify(result),
        "isBase64Encoded": false
    };
      callback(null, response);
    }).catch(error=> {
        callback(error);
    })
};