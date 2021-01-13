const slsk = require('slsk-client');
var app = require("express")();
var http = require('http').Server(app);
var bodyParser = require('body-parser');

const PORT = 9000;

function compare( a, b ) {
  let count = 0
  if ( a.speed < b.speed ){
    count--;
  }
  if ( a.speed > b.speed ){
    count++;
  }
  if ( a.bitrate < b.bitrate ) {
    count -= 2;
  }
  if ( a.bitrate > b.bitrate ) {
    count == 2;
  }
  return count;
}

console.log("STARTING SERVER CODE");

function download(client, file, output) {
  console.log("HIT HERE")
  try {
    client.download({
      file,
      path: output,
    }, (err, data) => {
      if (err) {
        console.log(err);
        return;
      }
      console.log("FINISHED DOWNLOADING!");
      return;
    });
  } catch (e) {
    console.log("ERROR: ", e);
    return;
  }
}

app.use(bodyParser.json())
app.post('/download',function(req,res){
  console.log("USER REQUESTED DOWNLOAD");

  if (!req.body) {
    return res.end();
  }

  const outputPath = req.body.outputPath;
  const user = req.body.user;
  const pass = req.body.pass;
  const files = req.body.files;

  console.log(req.body);

  if (!user || !pass || !files || !outputPath) {
    return res.status(403).json({ status: 'failure', error: "Bad request" });
  }

  try {
    slsk.connect({
      timeout: 10000,
      user,
      pass,
    }, (err, client) => {
      if (err) {
        console.log(client, "SOULSEEK GET CLIENT: ", err);
        return res.send({ error: err.message, line: err.lineNumber, name: err.name });
      }

      for (const file in files) {
        try {
          client.search({
            req: files[file],
            timeout: 30000
          }, (err, files) => {
            if (err) {
              console.log("SOULSEEK SEARCH SAYS: ", err);
              return res.end();
            }
            console.log("HERE!!");
            if (file) {
              console.log(files[file])
              const output = outputPath + "/temp/" + files[file].replace(/\\/g, "/");
              files.sort(compare);
              console.log("compare done!");
              download(client, files[0], output);
              return res.send(200);
            } else {
              console.log("No files found for ", file);
              return res.end();
            }
          })
        } catch (e) {
          console.log("SOULSEEK CLIENT SAYS: ", e)
          return res.end();
        }
      }

      return res.end();
    })
  } catch (e) {
    console.log("SOULSEEK CONNECTION ERROR: ", e)
    return res.end();
  }
});

http.listen(PORT, function(){
  console.log('listening on port ', PORT);
});
