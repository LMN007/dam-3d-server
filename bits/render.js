class CanvasManager {
    canvas = null
    w = 0;
    h = 0;
    pickPosition = {
        x: 0,
        y: 0
    };
    frame = null;

    constructor(frame, canvas) {
        this.clearPickPosition();
        this.canvas = canvas;
        this.w = frame.clientWidth;
        this.h = frame.clientHeight;
        frame.appendChild(canvas);
        frame.mouseout = ()=> this.clearPickPosition();
        this.frame = frame
    }

    Aspect() {
        return this.w / this.h
    }

    getCanvasRelativePosition(event) {
        const rect = this.canvas.getBoundingClientRect();
        return {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
        };
    }

    setPickPosition(event) {
        let pickPosition = this.pickPosition
        const pos = this.getCanvasRelativePosition(event);
        pickPosition.x = (pos.x / this.w) *  2 - 1;
        pickPosition.y = (pos.y / this.h) * -2 + 1;  // note we flip Y
    }

    clearPickPosition() {
        let pickPosition = this.pickPosition
        pickPosition.x = -100000;
        pickPosition.y = -100000;
    }
}

const frame = document.getElementById('canvas-frame');
const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer({antialias : true, powerPreference:'high-performance', alpha: true});
const canvas = new CanvasManager(frame, renderer.domElement, renderer);
const camera = new THREE.PerspectiveCamera(75, canvas.Aspect(), 0.1, 1000);
// const textureSky = new THREE.CubeTextureLoader().setPath( '../assets/static/skybox/' ).load( [
//     'hills2_rt_px.png',
//     'hills2_lf_nx.png',
//     'hills2_up_py.png',
//     'hills2_dn_ny.png',
//     'hills2_ft_pz.png',
//     'hills2_bk_nz.png'
// ] );
let clock = new THREE.Clock();

renderer.setSize(canvas.w, canvas.h);

renderer.setClearColor(0x222222, 0.0);

// camera.position.x = 0;
// camera.position.y = 0.15;
// camera.position.z = 2.60;
camera.position.x = 0;
camera.position.y = 0;
camera.position.z = 5;


const ambientLight = new THREE.AmbientLight( 0x404040 ); // soft white light
scene.add( ambientLight );
const light = new THREE.PointLight( 0xffffff, 1, 100 );
light.position.set( 20, 20, 20 );
scene.add( light );
const plight = new THREE.PointLight( 0xffffff, 1, 200 );
plight.position.set( -40, 20, 20 );
scene.add( plight );

function getLight(type,position,color,intensity,distance,decay,angle,penumbra){
    let light;
    switch (type) {
        case 0:
            light = new THREE.AmbientLight(color,intensity,distance,decay);
            break;
        case 1:
            light = new THREE.PointLight(color,intensity,distance,decay);
            break;
    }
    light.position.set(position[0],position[1],position[2]);
    return light;
    // light.penumbra = penumbra;
    // light.angle = angle;
}

scene.add(getLight(0,[0,0,0],0x404040,1,0,1,Math.PI/2,0));
scene.add(getLight(1,[18,18,18],0xffffff,1,100,1,Math.PI/2,0));
scene.add(getLight(1,[-30,18,18],0xffffff,1,200,1,Math.PI/2,0));
scene.add(getLight(1,[10,10,20],0xe0e0e0,6,200,1,Math.PI/2,0));
scene.add(getLight(1,[-10,-10,10],0xe0e0e0,5,200,1,Math.PI/2,0));
scene.add(getLight(1,[10,10,10],0xe0e0e0,4,200,1,Math.PI/2,0));
scene.add(getLight(1,[-10,-10,-10],0xe0e0e0,8,200,1,Math.PI/2,0));

let modelInfo = {
    vertices : 0,
    triangles :0,
    textures: 0,
    materials: 0,
    tangent_layers: false,
    uv_layers : false,
    maps : {
    },
    scale: 1,
};
let snapshot = "";
let count = 0;
let mixer = null;
function render() {
    // requestAnimationFrame(render);
    renderer.render(scene, camera);
    // var delta = clock.getDelta();
    // if (mixer != null) {
    //     mixer.update(delta);
    // }
    // if(count === 0)
    //     console.log(scene);
    // count++;
}

const loader = new THREE.GLTFLoader();
function loadgltf(url){
    loader.load(url, (m)=>{
        m.scene.traverse(obj =>{
            if(obj instanceof THREE.Mesh) {
                // obj.material.envMap  = textureSky;
                obj.material.needsUpdate  = true;
                modelInfo.vertices += obj.geometry.attributes.position.count;
                modelInfo.triangles += obj.geometry.index.count / 3;

                if (obj.geometry.attributes.tangent !== null && obj.geometry.attributes.tangent !== undefined)
                {
                    modelInfo.tangent_layers = true;
                }
                if (obj.geometry.attributes.uv !== null && obj.geometry.attributes.uv !== undefined)
                {
                    modelInfo.uv_layers = true;
                }
                if (obj.material !== null && obj.material !== undefined)
                {
                    modelInfo.materials++;
                    for(let x in obj.material)
                    {
                        if(obj.material[x] instanceof THREE.Texture)
                        {
                            modelInfo.textures++;
                            if(x.match(".+Map"))
                            {
                                modelInfo.maps[x] = true;
                            }
                        }
                    }
                }
            }
        });
        let box = new THREE.Box3();

        // 1
        // box.setFromObject(m.scene);
        // const vec = box.max.clone().sub(box.min);
        // // let scale = 0.000296;
        // let scale = 10 / Math.max(vec.x,vec.y,vec.z);
        // modelInfo.scale = scale;
        // m.scene.scale.set(scale, scale, scale);
        //
        // box.setFromObject(m.scene);
        // const mid = box.max.clone().add(box.min).multiplyScalar((0.5));
        // m.scene.position.set(-mid.x,-mid.y,-mid.z);





        // 2
        box.setFromObject(m.scene);
        const vec = box.max.clone();
        // const vec = box.max.clone().sub(box.min);
        console.log(box.max);
        console.log(box.min);
        console.log(vec);
        // let scale = 0.000296;
        let scale = 5 / Math.max(vec.x,vec.y,vec.z);
        modelInfo.scale = scale;
        m.scene.scale.set(scale, scale, scale);

        box.setFromObject(m.scene);
        const mid = box.max.clone().add(box.min).multiplyScalar((0.5));
        m.scene.position.set(-mid.x,-mid.y,-mid.z);


        console.log(vec);
        // console.log(mid);
        console.log(scale);
        console.log(m.scene.position);
        console.log(m.scene);
        console.log(m);


        scene.add(m.scene);
        if(m.animations !== undefined && m.animations !== null && m.animations.length > 0)
        {
            mixer = new THREE.AnimationMixer(m.scene);
            mixer.clipAction(m.animations[0]).play();
            console.log("animation");
        }
        render();
        snapshot = canvas.canvas.toDataURL();
        // scene.remove(m.scene);



        let infoDiv = document.createElement("div");
        infoDiv.id = "model-info";
        let snapshotDiv = document.createElement("div");
        snapshotDiv.id = "snapshot";

        for(let x in modelInfo)
        {
            let div = document.createElement("div");
            div.id = x;
            if( modelInfo[x] instanceof Object)
            {
                for(let y in modelInfo[x])
                {
                   let div_child = document.createElement("div");
                   div_child.id = y;
                   div_child.innerText = modelInfo[x][y];
                   div.appendChild(div_child);
                }
            }
            else
                div.innerText = modelInfo[x];
            infoDiv.appendChild(div);
        }
        snapshotDiv.innerText = snapshot;
        document.body.append(infoDiv);
        document.body.append(snapshotDiv);
    });
}
function init() {
    modelInfo = {
        vertices : 0,
        triangles :0,
        textures: 0,
        materials: 0,
        tangent_layers: false,
        uv_layers : false,
        maps : {
        },
        scale: 1,
    };
    snapshot = "";
    document.body.removeChild(document.getElementById('model-info'));
    document.body.removeChild(document.getElementById('snapshot'));

}