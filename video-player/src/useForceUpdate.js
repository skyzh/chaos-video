import { useState } from "react";

const useForceUpdate = () => {
  const [, setState] = useState();
  return setState;
};

export default useForceUpdate;
