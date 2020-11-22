import "./App.scss";
import Container from "react-bootstrap/Container";
import ReactHlsPlayer from "react-hls-player";
import { useRef, useEffect } from "react";

// function sync() {
//   if (videos.b.media.readyState === 4) {
//     videos.b.currentTime(
//       videos.a.currentTime()
//     );
//   }
//   requestAnimationFrame(sync);
// }

function App() {
  const ref1 = useRef();
  const ref2 = useRef();
  const ref3 = useRef();
  const ref4 = useRef();

  const canplay = (event) => console.log(event);

  const refs = [ref1, ref2, ref3, ref4];
  const MAIN_ID = "ref4";

  const seek = ({ target }) => {
    if (target.id !== MAIN_ID) return;
    for (let ref of refs) {
      if (ref.current.id !== MAIN_ID) {
        ref.current.currentTime = target.currentTime;
      }
    }
  };

  const play = ({ target }) => {
    if (target.id !== MAIN_ID) return;
    for (let ref of refs) {
      if (ref.current.id !== MAIN_ID) {
        ref.current.play();
      }
    }
  };

  const pause = ({ target }) => {
    if (target.id !== MAIN_ID) return;
    for (let ref of refs) {
      if (ref.current.id !== MAIN_ID) {
        ref.current.pause();
      }
      ref.current.currentTime = target.currentTime;
    }
  };

  // const requestRef = useRef();

  // const animate = (time) => {
  //   let currentTime = 0;
  //   for (let ref of refs) {
  //     if (ref.current.id == MAIN_ID) {
  //       currentTime = ref.current.currentTime;
  //     }
  //   }
  //   for (let ref of refs) {
  //     if (ref.current.id !== MAIN_ID) {
  //       ref.current.currentTime = currentTime;
  //     }
  //   }
  //   // The 'state' will always be the initial value here
  //   requestRef.current = requestAnimationFrame(animate);
  // };

  // useEffect(() => {
  //   requestRef.current = requestAnimationFrame(animate);
  //   return () => cancelAnimationFrame(requestRef.current);
  // }, []); // Make sure the effect runs only once

  useEffect(() => {
    const callbacks = [];
    for (let ref of refs) {
      if (ref.current) {
        ref.current.addEventListener("canplay", canplay);
        ref.current.addEventListener("seeked", seek);
        ref.current.addEventListener("play", play);
        ref.current.addEventListener("pause", pause);

        callbacks.push(() => {
          ref.current.removeEventListener("canplay", canplay);
          ref.current.removeEventListener("seeked", seek);
          ref.current.removeEventListener("play", play);
          ref.current.removeEventListener("pause", pause);
        });
      }
    }
    return () => {
      for (let callback of callbacks) callback();
    };
  });

  return (
    <Container className="chaos-video-container">
      <ReactHlsPlayer
        url="/data/video-stream/chunk_0_0/video_c_0_0.mp4_1125.m3u8"
        autoplay={false}
        controls={false}
        playerRef={ref1}
        id="ref1"
        className="chaos-video-element"
      />
      <ReactHlsPlayer
        url="/data/video-stream/chunk_1_0/video_c_1_0.mp4_1125.m3u8"
        autoplay={false}
        controls={false}
        playerRef={ref2}
        id="ref2"
        className="chaos-video-element"
      />
      <ReactHlsPlayer
        url="/data/video-stream/chunk_2_0/video_c_2_0.mp4_1125.m3u8"
        autoplay={false}
        controls={false}
        playerRef={ref3}
        id="ref3"
        className="chaos-video-element"
      />
      <ReactHlsPlayer
        url="/data/video-stream/chunk_3_0/video_c_3_0.mp4_1125.m3u8"
        autoplay={false}
        controls={true}
        playerRef={ref4}
        id="ref4"
        className="chaos-video-element"
      />
    </Container>
  );
}

export default App;
