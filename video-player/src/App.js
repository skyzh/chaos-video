import "./App.scss";
import Container from "react-bootstrap/Container";
import ReactHlsPlayer from "react-hls-player";
import { useRef, useEffect, createRef } from "react";
import Button from "react-bootstrap/Button";
import StreamChart from "./streamChart";

import range from "lodash/range";
import min from "lodash/min";
import max from "lodash/max";
import every from "lodash/every";
import clone from "lodash/clone";

import CustomAbrController from "./AbrController";
import { currentLevels } from "./AbrController";
import { globalBandwidth } from "./EwmaBandWidthEstimator.ts";

import { append } from "./utils.ts";

const maxChartTicks = 10;
const maxWidthTicks = 60;
const maxFrameBuffer = 12;
const maxBufferChartTicks = 160;
const bufferTickWidth = 3;
const bufferHeight = 100;

let frames = [];
let canvasDrop = [];

function genAbrConfig(idx) {
  return {
    idx,
    testBandwidth: false,
    abrController: CustomAbrController,
  };
}

function getFrame(time) {
  // return Math.floor(time * 60)
  return Math.floor(time * 29.97);
}

function fillCanvasRect(canvas, y, x1, xwidth, color) {
  const ctx = canvas.getContext("2d");
  ctx.beginPath();
  ctx.rect(
    x1 * bufferTickWidth,
    (bufferHeight / 4) * y,
    bufferTickWidth * xwidth,
    bufferHeight / 4
  );
  ctx.fillStyle = color;
  ctx.fill();
}

function frameReady(frame) {
  const idx = frame % maxFrameBuffer;
  const recordFrame = canvasDrop[idx].frame;
  if (recordFrame !== frame) {
    canvasDrop[idx].frame = frame;
    canvasDrop[idx].ready = 0;
  }
  canvasDrop[idx].ready += 1;
}

let playableSegment = [];

function App() {
  const ref1 = useRef();
  const ref2 = useRef();
  const ref3 = useRef();
  const ref4 = useRef();
  const requestRef = useRef();
  const requestRefs = useRef([]);
  const canvasRef = useRef([]);
  const finalCanvasRef = useRef();
  const bufferCanvasRef = useRef();

  const canplay = ({ target }) => {
    playableSegment[target.id] = true;
    if (every(playableSegment, Boolean)) {
      play();
    }
  };

  const waiting = ({ target }) => {
    console.log("waiting!", target.id);
    // playableSegment[target.id] = false
    // pause()
  };

  const refs = [ref1, ref2, ref3, ref4];
  const MAIN_ID = "ref1";
  const mainRef = ref1;

  const series = useRef(
    range(refs.length + 1).map((idx) => ({
      data: range(maxChartTicks).map((_x) => 0),
      name: idx < refs.length ? `Stream ${idx}` : `Final Stream`,
    }))
  );

  const widthSeries = useRef(
    range(refs.length).map((idx) => ({
      data: range(maxWidthTicks).map((_x) => 0),
      name: `Stream ${idx}`,
    }))
  );

  const qualitySeries = useRef(clone(globalBandwidth));

  if (canvasRef.current.length !== maxFrameBuffer) {
    canvasRef.current = Array(maxFrameBuffer)
      .fill()
      .map((_, i) => canvasRef.current[i] || createRef());
  }

  if (canvasDrop.length !== maxFrameBuffer) {
    canvasDrop = Array(maxFrameBuffer)
      .fill()
      .map((_, i) => ({ frame: -1, ready: 0 }));
  }

  if (requestRefs.current.length !== refs.length) {
    requestRefs.current = Array(refs.length)
      .fill()
      .map((_, i) => requestRefs.current[i] || createRef());
  }

  if (frames.length !== refs.length) {
    frames = Array(refs.length)
      .fill()
      .map((_, i) => 0);
  }

  if (playableSegment.length !== refs.length) {
    playableSegment = Array(refs.length)
      .fill()
      .map((_, i) => false);
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
      if (canvasRef.current) {
        const minFrame = min(frames);
        const maxFrame = max(frames);

        let bufferCanvas = bufferCanvasRef.current;

        for (let idx = 0; idx < refs.length; idx++) {
          const frame = frames[idx];
          append(series.current[idx].data, frame, maxChartTicks);
          if (frame % 60 == 0) {
            append(
              widthSeries.current[idx].data,
              currentLevels[idx] || 0,
              maxWidthTicks
            );
          }

          if (bufferCanvas) {
            fillCanvasRect(
              bufferCanvas,
              idx,
              (maxFrame + 1) % maxBufferChartTicks,
              10,
              "#FFFFFF"
            );
          }
        }

        if (series.current) {
          append(series.current[refs.length].data, minFrame, maxChartTicks);
        }

        if (finalCanvasRef.current) {
          const idx = minFrame % maxFrameBuffer;
          // console.log(canvasDrop[idx])
          if (canvasDrop[idx].ready === refs.length) {
            const ctx = finalCanvasRef.current.getContext("2d");
            let thisCanvas = canvasRef.current[idx];
            if (thisCanvas && thisCanvas.current) {
              ctx.drawImage(thisCanvas.current, 0, 0, width, height);
            }
          }
        }
      }

      if (qualitySeries.current) {
        qualitySeries.current = clone(globalBandwidth);
      }
      requestRef.current = requestAnimationFrame(animate);
    };

    const videoCallback = (idx) => {
      const func = (now, metadata) => {
        const time = metadata.mediaTime;
        const frame = getFrame(time);
        const lstFrame = frames[idx];
        frames[idx] = frame;
        const ref = refs[idx];
        const minFrame = min(frames);
        if (frame >= minFrame + maxFrameBuffer) {
          console.log("cannot follow up!");
          playableSegment[idx] = false;
          pause();
          setTimeout(() => play(), 1000);
        } else {
          let bufferCanvas = bufferCanvasRef.current;

          if (bufferCanvas) {
            for (let frame_ = lstFrame + 1; frame_ < frame; frame_ += 1) {
              fillCanvasRect(
                bufferCanvas,
                idx,
                frame_ % maxBufferChartTicks,
                1,
                "#F6D55C"
              );
            }
          }

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
            frameReady(frame);
          }

          if (bufferCanvas) {
            fillCanvasRect(
              bufferCanvas,
              idx,
              frame % maxBufferChartTicks,
              1,
              "#3CAEA3"
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
  });

  useEffect(() => {
    const callbacks = [];
    for (let ref of refs) {
      if (ref.current) {
        if (ref.current.id !== MAIN_ID) {
          ref.current.muted = true;
        }

        ref.current.addEventListener("canplay", canplay);
        ref.current.addEventListener("waiting", waiting);

        callbacks.push(() => {
          ref.current.removeEventListener("canplay", canplay);
          ref.current.removeEventListener("waiting", waiting);
        });
      }
    }
    return () => {
      for (let callback of callbacks) callback();
    };
  });

  const video_urls = range(4).map(
    (idx) =>
      `/data/zelda/chunk_${idx}_0/zelda_trailer_c_${idx}_0.mp4_master.m3u8`
  );
  // const video_urls = range(4).map(idx => `/data/genshin/chunk_${idx}_0/genshin_c_${idx}_0.mp4_master.m3u8`)

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
      hlsConfig={genAbrConfig(i)}
      className="chaos-video-element"
    />
  ));
  return (
    <Container fluid className="chaos-video-container">
      <div className="row">
        <div className="col">
          <h4>Composite Video</h4>
          <canvas width={width} height={height} ref={finalCanvasRef}></canvas>
          {frameBuffer}
        </div>
        <div className="col">
          <h4>Original Split Video</h4>
          {videoBuffer}
          <div>
            <Button variant="primary" onClick={play} className="mr-1">
              Play
            </Button>
            <Button variant="primary" onClick={pause} className="mr-1">
              Pause
            </Button>
            <Button
              variant="primary"
              onClick={() => seek(10.0)}
              className="mr-1"
            >
              Seek
            </Button>
          </div>
        </div>
      </div>

      <div className="row mt-3">
        <div className="col-4">
          <h4>Video Lag</h4>
          <StreamChart
            id="lag"
            series={series.current}
            type="line"
          ></StreamChart>
        </div>
        <div className="col-4">
          <h4>Buffer Health</h4>
          <canvas
            width={maxBufferChartTicks * bufferTickWidth}
            height={bufferHeight}
            ref={bufferCanvasRef}
          ></canvas>
        </div>
        <div className="col-4">
          <h4>Video Quality</h4>
          <StreamChart
            id="quality"
            series={widthSeries.current}
            type="line"
          ></StreamChart>
          <h4>Video Bandwidth</h4>
          {/* <StreamChart id="bandwidth" series={qualitySeries.current} type="line"></StreamChart> */}
        </div>
      </div>
    </Container>
  );
}

export default App;
