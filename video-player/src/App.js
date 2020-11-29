import "./App.scss";
import Container from "react-bootstrap/Container";
import ReactHlsPlayer from "react-hls-player";
import { useRef, useEffect, createRef } from "react";
import range from "lodash/range";
import min from "lodash/min";
import Button from "react-bootstrap/Button";
import StreamChart from "./streamChart";
import useForceUpdate from "./useForceUpdate";

// function sync() {
//   if (videos.b.media.readyState === 4) {
//     videos.b.currentTime(
//       videos.a.currentTime()
//     );
//   }
//   requestAnimationFrame(sync);
// }

let playTime = Date.now();
let currentTime = 0;

const maxChartTicks = 10;
const maxFrameBuffer = 8;
let frames = [];

function append(data, x) {
  data.push(x);
  if (data.length > maxChartTicks) {
    data.splice(0, data.length - maxChartTicks);
  }
}

function getFrame(time) {
  // return Math.floor(time * 60)
  return Math.floor(time * 29.97);
}

function App() {
  const ref1 = useRef();
  const ref2 = useRef();
  const ref3 = useRef();
  const ref4 = useRef();
  const requestRef = useRef();
  const requestRefs = useRef([]);
  const canvasRef = useRef([]);
  const finalCanvasRef = useRef();

  const canplay = (event) => console.log(event);

  const refs = [ref1, ref2, ref3, ref4];
  const MAIN_ID = "ref1";
  const mainRef = ref1;

  const series = useRef(
    range(refs.length + 1).map((_x) => ({
      data: range(maxChartTicks).map((_x) => 0),
    }))
  );

  if (canvasRef.current.length !== maxFrameBuffer) {
    canvasRef.current = Array(maxFrameBuffer)
      .fill()
      .map((_, i) => canvasRef.current[i] || createRef());
  }

  if (requestRefs.current.length !== refs.length) {
    requestRefs.current = Array(refs.length)
      .fill()
      .map((_, i) => requestRefs.current[i] || createRef());
  }

  if (frames.length != refs.length) {
    frames = Array(refs.length)
      .fill()
      .map((_, i) => 0);
  }

  const seek = (currentTime) => {
    pause();
    for (let ref of refs) {
      ref.current.currentTime = currentTime;
    }
    play();
  };

  const play = () => {
    for (let ref of refs) {
      ref.current.currentTime = mainRef.current.currentTime;
      ref.current.play();
    }
    playTime = currentTime;
  };

  const pause = () => {
    for (let ref of refs) {
      ref.current.pause();
      ref.current.currentTime = mainRef.current.currentTime;
    }
  };

  const width = 1920 / 2;
  const height = 1080 / 2;

  useEffect(() => {
    const animate = (time) => {
      currentTime = Date.now();

      if (canvasRef.current) {
        const minFrame = min(frames);

        for (let i = 0; i < refs.length; i++) {
          const frame = frames[i];
          append(series.current[i].data, frame);
        }

        if (series.current) {
          append(series.current[refs.length].data, minFrame);
        }

        if (finalCanvasRef.current) {
          const ctx = finalCanvasRef.current.getContext("2d");
          let thisCanvas = canvasRef.current[minFrame % maxFrameBuffer];
          if (thisCanvas && thisCanvas.current) {
            ctx.drawImage(thisCanvas.current, 0, 0, width, height);
          }
        }
      }

      requestRef.current = requestAnimationFrame(animate);
    };

    const videoCallback = (idx) => {
      const func = (now, metadata) => {
        const time = metadata.mediaTime;
        const delay = metadata.expectedDisplayTime - now;
        const frame = getFrame(time);
        frames[idx] = frame;
        const ref = refs[idx];
        const minFrame = min(frames);
        if (frame >= minFrame + maxFrameBuffer) {
          console.log("cannot follow up!");
        } else {
          let thisCanvas = canvasRef.current[frame % maxFrameBuffer];
          if (thisCanvas && thisCanvas.current) {
            const ctx = thisCanvas.current.getContext("2d");
            ctx.drawImage(
              ref.current,
              0,
              Math.floor((height * idx) / refs.length),
              width,
              Math.floor(height / refs.length)
            );
          }
        }
        requestRefs.current[idx].current = refs[
          idx
        ].current.requestVideoFrameCallback(func);
      };
      return func;
    };

    requestRef.current = requestAnimationFrame(animate);

    for (let i = 0; i < refs.length; i++) {
      requestRefs.current[i].current = refs[
        i
      ].current.requestVideoFrameCallback(videoCallback(i));
    }

    return () => {
      cancelAnimationFrame(requestRef.current);
      for (let i = 0; i < refs.length; i++) {
        refs[i].current.cancelVideoFrameCallback(
          requestRefs.current[i].current
        );
      }
    };
  }, []);

  useEffect(() => {
    const callbacks = [];
    for (let ref of refs) {
      if (ref.current) {
        if (ref.current.id != MAIN_ID) {
          ref.current.muted = true;
        }

        ref.current.addEventListener("canplay", canplay);

        callbacks.push(() => {
          ref.current.removeEventListener("canplay", canplay);
        });
      }
    }
    return () => {
      for (let callback of callbacks) callback();
    };
  });

  const video_urls = range(4).map(
    (idx) => `/data/zelda/chunk_${idx}_0/zelda_trailer_c_${idx}_0.mp4_1197.m3u8`
  );
  // const video_urls = range(2).map(idx => `/data/genshin/chunk_${idx}_0/genshin_c_${idx}_0.mp4_master.m3u8`)

  const frameBuffer = range(maxFrameBuffer).map((i) => (
    <canvas
      width={width}
      height={height}
      ref={canvasRef.current[i]}
      key={i}
      className="d-none"
    ></canvas>
  ));
  const videoBuffer = range(refs.length).map((i) => (
    <ReactHlsPlayer
      key={i}
      url={video_urls[i]}
      autoplay={false}
      controls={false}
      playerRef={refs[i]}
      id={`ref${i}`}
      className="chaos-video-element"
    />
  ));
  return (
    <Container fluid className="chaos-video-container">
      <div className="row">
        <div className="col">
          <canvas width={width} height={height} ref={finalCanvasRef}></canvas>
          {frameBuffer}
        </div>
        <div className="col">{videoBuffer}</div>
      </div>

      <div>
        <Button variant="primary" onClick={play}>
          Play
        </Button>
        <Button variant="primary" onClick={pause}>
          Pause
        </Button>
        <Button variant="primary" onClick={() => seek(10.0)}>
          Seek
        </Button>
      </div>
      <div>
        <StreamChart series={series.current}></StreamChart>
      </div>
    </Container>
  );
}

export default App;
