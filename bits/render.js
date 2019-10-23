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
const textureSky = new THREE.CubeTextureLoader().setPath( './assets/static/skybox/' ).load( [
    'hills2_rt_px.png',
    'hills2_lf_nx.png',
    'hills2_up_py.png',
    'hills2_dn_ny.png',
    'hills2_ft_pz.png',
    'hills2_bk_nz.png'
] );


renderer.setSize(canvas.w, canvas.h);

renderer.setClearColor(0x222222, 0.0);

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


function render() {
    requestAnimationFrame(render);
    renderer.render(scene, camera);
}

const loader = new THREE.GLTFLoader();
// loadgltf("./models/vysehrad_-_statue_of_zaboj_and_slavoj/scene.gltf");
// loadgltf("./models/3dinktober2019-ash/scene.gltf");
// loadgltf("./models/toon_female_base_mesh/scene.gltf");
// loadgltf("./models/paladin_sword/scene.gltf ");
// loadgltf("./unzipped/b4f49c98/scene.gltf ");
function loadgltf(url){
    loader.load(url, (m)=>{
        m.scene.traverse(obj =>{
            if(obj instanceof THREE.Mesh) {
                obj.material.envMap  = textureSky;
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
        box.setFromObject(m.scene);

        let vec = box.max.clone().sub(box.min);
        console.log(vec);
        let scale = 0.000296;
        // let scale = 5 / Math.max(vec.x,vec.y,vec.z);
        modelInfo.scale = scale;
        m.scene.scale.set(scale, scale, scale);

        box.setFromObject(m.scene);
        const mid = box.max.clone().add(box.min).multiplyScalar((0.5));
        console.log(m.scene.position);
        // m.scene.position.set(-mid.x,-mid.y,-mid.z);

        console.log(mid);
        console.log(m.scene);
        console.log(scale);

        scene.add(m.scene);
        render();
        snapshot = canvas.canvas.toDataURL();
        scene.remove(m.scene);



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