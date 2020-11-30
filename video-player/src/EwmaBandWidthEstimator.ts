/*
 * EWMA Bandwidth Estimator
 *  - heavily inspired from shaka-player
 * Tracks bandwidth samples and estimates available bandwidth.
 * Based on the minimum of two exponentially-weighted moving averages with
 * different half-lives.
 */

import EWMA from "./EWMA";
import map from "lodash/map";
import sum from "lodash/sum";
import range from "lodash/range";

import { append } from "./utils";

const bandwidthHistory = 20;
export const globalBandwidth = [
  { data: range(bandwidthHistory).map((_) => 0), name: "Fast" },
  { data: range(bandwidthHistory).map((_) => 0), name: "Slow" },
];

class GlobalEwmaBandWidthEstimator {
  private defaultEstimate_: number;
  private minWeight_: number;
  private minDelayMs_: number;
  private slow_: EWMA[];
  private fast_: EWMA[];
  private length_: number;

  // TODO(typescript-hls)
  constructor(
    slow: number,
    fast: number,
    defaultEstimate: number,
    length: number
  ) {
    this.defaultEstimate_ = defaultEstimate;
    this.minWeight_ = 0.001 * length;
    this.minDelayMs_ = 50;
    this.slow_ = map(range(length), () => new EWMA(slow));
    this.fast_ = map(range(length), () => new EWMA(fast));
    this.length_ = length;
  }

  sample(durationMs: number, numBytes: number, idx: number) {
    durationMs = Math.max(durationMs, this.minDelayMs_);
    let numBits = 8 * numBytes,
      // weight is duration in seconds
      durationS = durationMs / 1000,
      // value is bandwidth in bits/s
      bandwidthInBps = numBits / durationS;
    this.fast_[idx].sample(durationS, bandwidthInBps);
    this.slow_[idx].sample(durationS, bandwidthInBps);
  }

  canEstimate(): boolean {
    let fast = this.fast_;
    return fast && sum(map(fast, (x) => x.getTotalWeight())) >= this.minWeight_;
  }

  getEstimate(): number {
    if (this.canEstimate()) {
      // console.log('slow estimate:'+ Math.round(this.slow_.getEstimate()));
      // console.log('fast estimate:'+ Math.round(this.fast_.getEstimate()));
      // Take the minimum of these two estimates.  This should have the effect of
      // adapting down quickly, but up more slowly.
      const fastEstimate =
        sum(map(this.fast_, (x) => x.getEstimate())) / this.length_;
      const slowEstimate =
        sum(map(this.slow_, (x) => x.getEstimate())) / this.length_;
      append(
        globalBandwidth[0].data,
        fastEstimate / 1024 / 1024,
        bandwidthHistory
      );
      append(
        globalBandwidth[1].data,
        slowEstimate / 1024 / 1024,
        bandwidthHistory
      );

      return Math.min(fastEstimate, slowEstimate);
    } else {
      return this.defaultEstimate_;
    }
  }

  destroy() {}
}

let globalEwmaBandWidthEstimator: GlobalEwmaBandWidthEstimator | null = null;

const videoStreamNum = 4;

function getGlobalEwmaBandWidthEstimator(
  hls: any,
  slow: number,
  fast: number,
  defaultEstimate: number
) {
  if (globalEwmaBandWidthEstimator == null) {
    globalEwmaBandWidthEstimator = new GlobalEwmaBandWidthEstimator(
      slow,
      fast,
      defaultEstimate,
      videoStreamNum
    );
  }
  return globalEwmaBandWidthEstimator;
}

export default getGlobalEwmaBandWidthEstimator;
