const { S3Client, GetObjectCommand } = require("@aws-sdk/client-s3");
const region = "us-east-1";
const client = new S3Client({ region });

exports.handler = async (event) => {
    try {
		const command = new GetObjectCommand({
			Bucket: "event['bucket']",
			Key: "data.json",
		});
		const results = await client.send(command);

	} catch (err) {
		var results=err;
		return results;
	}
    const response = {
        statusCode: 200,
        body: JSON.stringify(results),
    };
    return JSON.stringify(results);
};

  //const { Body } = await client.send(command);
  //const bodyContents = await streamToString(Body);
  //console.log(bodyContents);
