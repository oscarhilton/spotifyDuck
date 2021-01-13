const slsk = require('slsk-client');
const Hub = require("socket.engine").Hub;
const fs = require('fs');

const CONFIG_TXT = 'config.txt';
const NOT_DOWNLOAD_FILES_TXT = 'not_download.txt';

function compare( a, b ) {
  let count = 0
  if ( a.speed < b.speed ){
    count--;
  }
  if ( a.speed > b.speed ){
    count++;
  }
  if ( a.bitrate < b.bitrate ) {
    count--
  }
  if ( a.bitrate > b.bitrate ) {
    count++;
  }
  return count;
}

async function slskConnection(username, password, location, list) {
  return await slsk.connect({
    timeout: 2000,
    user: username,
    pass: password,
  }, (err, client) => {
    if (err) return console.log("SOULSEEK GET CLIENT: ", err);

    for (item of list) {
      client.search({
        req: item,
        timeout: 5000 // you can increase if you want a deeper search
      }, (err, res) => {
          if (err) return console.log(err)
      })
    }
    // use event function
    client.on('found', function(result) {
      console.log(result);
    });
  });
}

fs.readFile(CONFIG_TXT, 'utf8' , (err, data) => {
  if (err) {
    console.error(err)
    return
  }

  const { username, password, location } = JSON.parse(data);

  fs.readFile(NOT_DOWNLOAD_FILES_TXT, 'utf8' , async (err, data) => {
    if (err) {
      console.error(err)
      return
    }
  
    const filesToDownload = JSON.parse(data);
  
    let downloadList = [];
    for (const file of filesToDownload) {
      const { Album, Track, Artist } = file;
      const searchForThis = (Album === Track) ? Track + ' ' + Artist : Album + ' ' + Track;
      downloadList.push(searchForThis);
    }
    console.log(downloadList);
    return slskConnection(username, password, location, downloadList);
  });
  return;
});

console.log("HERE");


const h = new Hub(9000);

console.log("START")

h.on("Transport", (data) => {
  console.log("Hub connected!");
});

h.on("hello", (data) => {
  console.log(data);
  h.close();
});

// console.log("STARTING SERVER CODE");

// function download(client, file, output) {
//   console.log("HIT HERE")
//   try {
//     client.download({
//       file,
//       path: output,
//     }, (err, data) => {
//       if (err) {
//         console.log(err);
//         return;
//       }
//       console.log("FINISHED DOWNLOADING!");
//       return;
//     });
//   } catch (e) {
//     console.log("ERROR: ", e);
//     return;
//   }
// }

// app.use(bodyParser.json())
// app.post('/download',function(req,res){
//   console.log("USER REQUESTED DOWNLOAD");

//   if (!req.body) {
//     return res.status(403).json({ status: '403', error: "Bad request" });
//   }

//   const outputPath = req.body.outputPath;
//   const user = req.body.user;
//   const pass = req.body.pass;
//   const files = req.body.files;

//   console.log(req.body);

//   if (!user || !pass || !files || !outputPath) {
//     return res.status(403).json({ status: '403', error: "Bad request" });
//   }

//   try {
//     slsk.connect({
//       timeout: 10000,
//       user,
//       pass,
//     }, (err, client) => {
//       if (err) {
//         console.log(client, "SOULSEEK GET CLIENT: ", err);
//         return res.send({ error: err.message, line: err.lineNumber, name: err.name });
//       }

//       for (const file in files) {
//         console.log(file)
//         // try {
//         //   client.search({
//         //     req: files[file],
//         //     timeout: 30000
//         //   }, (err, files) => {
//         //     if (err) {
//         //       console.log("SOULSEEK SEARCH SAYS: ", err);
//         //       return res.end();
//         //     }
//         //     console.log("HERE!!");
//         //     if (file) {
//         //       console.log(files[file])
//         //       const output = outputPath + "/temp/" + files[file].replace(/\\/g, "/");
//         //       files.sort(compare);
//         //       console.log("compare done!");
//         //       download(client, files[0], output);
//         //     } else {
//         //       console.log("No files found for ", file);
//         //       return res.end();
//         //     }
//         //   })
//         // } catch (e) {
//         //   console.log("SOULSEEK CLIENT SAYS: ", e)
//         //   return res.end();
//         // }
//       }

//       return res.end();
//     })
//   } catch (e) {
//     console.log("SOULSEEK CONNECTION ERROR: ", e)
//     return res.end();
//   }
// });