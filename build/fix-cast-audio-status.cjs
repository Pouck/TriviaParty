const fs=require('fs');let s=fs.readFileSync('cast-receiver/receiver.js','utf8').replace(/\r\n/g,'\n');
s=s.replace('      enabled = false;\n      queued=[];', '      enabled = false;\n      if (options.onAudioStatus) options.onAudioStatus(error && error.name === "NotAllowedError" ? "blocked" : "error");\n      queued=[];');
s=s.replace('          enabled = true;\n          if (control)', '          enabled = true;\n          if (options.onAudioStatus) options.onAudioStatus("playing");\n          if (control)');
s=s.replace('    var render = makeRenderer(doc);\n    function ready(senderId)', `    var render = makeRenderer(doc, {onAudioStatus:function (status) {
      context.getSenders().forEach(function(sender) {
        context.sendCustomMessage(namespace, sender.senderId, {type:'audio-status', version:1, status:status});
      });
    }});
    function ready(senderId)`);
for(const dir of ['cast-receiver/','app/src/main/assets/tv/'])fs.writeFileSync(dir+'receiver.js',s);
