import "./App.scss";
import Container from "react-bootstrap/Container";
import ReactHlsPlayer from "react-hls-player";

function App() {
  return (
    <Container>
      <ReactHlsPlayer
        url="/data/output.m3u8"
        autoplay={false}
        controls={true}
      />
    </Container>
  );
}

export default App;
