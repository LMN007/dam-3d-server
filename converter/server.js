const express = require("express");
const app = express();

const cors = require("cors");
app.use(cors());

const bodyParser = require("body-parser");

const obj2gltf = require('obj2gltf');
const fbx2gltf = require('fbx2gltf');
const fs = require('fs');
const gltf_path = "";
const output_name = "scene.gltf"


app.listen(5300,()=>{
    console.log("---------server on ------------");
});

function deleteall(path) {
	var files = [];
	if(fs.existsSync(path)) {
		files = fs.readdirSync(path);
		files.forEach(function(file, index) {
			let curPath = path + "\\" + file;
			if(fs.statSync(curPath).isDirectory()) { // recurse
				deleteall(curPath);
			} else { // delete file
				fs.unlinkSync(curPath);
			}
		});
		fs.rmdirSync(path);
	}
};

app.post("/api/obj2gltf", bodyParser.json(), async (req,res) => {
	console.log(req.body);
	let src = req.body['src'];
	let dst = req.body['dst'];
	console.log("obj2gltf start");
	let ok = false;
	let converted = ""
	await obj2gltf(src).then(function (gltf) {
		let data = Buffer.from(JSON.stringify(gltf));
		fs.writeFileSync(dst+'\\'+output_name, data);
		ok = true;
		let files = fs.readdirSync(dst);
        files.forEach(function(file, index) {
            if(file.search('.gltf') < 0)
            {
                let curPath = dst + "\\" + file;
                if(fs.statSync(curPath).isDirectory()) { // recurse
                    deleteall(curPath);
                } else { // delete file
                    fs.unlinkSync(curPath);
                }
            }
        });
		converted = output_name
	});
	res.write(JSON.stringify({'ok':ok,'converted':converted}));
	res.end();
	// const src = req.body['src'];
	// const dst = req.body['dst'];
    // // const obj_name = './source/model';
    // obj2gltf(src_path)
    //     .then(function(gltf) {
    //         const data = Buffer.from(JSON.stringify(gltf));
    //         fs.writeFileSync(gltf_path+'/'+model_name+'.gltf', data);
    //     });
});


app.post("/api/fbx2gltf", bodyParser.json(), async (req,res) => {
	console.log(req.body);
	let src = req.body['src'];
	let dst = req.body['dst'];
	let ok = false;
	let converted = "";
	await fbx2gltf(src, dst+'\\'+output_name, ['--khr-materials-unlit']).then(
		destPath => {
			let files = fs.readdirSync(dst);
			files.forEach(function(file, index) {
				if(file.search(output_name.split('.')[0]+"_out") < 0)
				{
					let curPath = dst + "\\" + file;
					if(fs.statSync(curPath).isDirectory()) { // recurse
						deleteall(curPath);
					} else { // delete file
						fs.unlinkSync(curPath);
					}
				}
			});
			let oldpath = dst+'\\'+output_name.split('.')[0]+"_out"
			files = fs.readdirSync(oldpath)
			files.forEach(function(file, index) {
				fs.renameSync(oldpath+'\\' + file,dst + "\\"  + file)
			});
			fs.rmdirSync(oldpath);
			ok = true;
			converted = output_name;
			console.log("FBX2GLTF success ");
		},
		error => {
			console.log(error + " failed!");
		}
	);
	res.write(JSON.stringify({'ok':ok,'converted':converted}));
	res.end();
	// try{
	// 	console.log("fbx2gltf start");
	// 	const dstPath = await fbx2gltf(src, dst+'/scene.gltf', ['--khr-materials-unlit']);
	// 	res.write({
	// 		ok: true
	// 	})
	// 	console.log("success");
	// }
	// catch(e){
	// 	res.write({
	// 		ok:e
	// 	})
	// 	console.log("failed");
	// }
	
});
