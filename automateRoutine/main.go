// Copyright 2015 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

//This is a set of some individual programs which are useful for my dialy routines.
package main

import (
	"flag"
	"time"

	"github.com/Jack301/automateRoutine/automate/adjustTemperature"
	"github.com/Jack301/automateRoutine/automate/autoVocabulary"
)

var (
	checkNewWordInterval             int //interval for checking new words
	whetherEnableAdjustColorFunction int
	whetherEnableSeekNewWords        int
)

func init() {
	flag.IntVar(&checkNewWordInterval, "interval", 30, "interval for checking new words.")
	flag.IntVar(&whetherEnableAdjustColorFunction, "adjustcolor", 0, "Please chose whether to enable the functionality of automatically adjust computer color temperature.")
	flag.IntVar(&whetherEnableSeekNewWords, "seekNewWords ", 1, "chose whether to enable the functionality of automatically seek new words in the historical record file of goldendict.")

	flag.String("help", "", "command help")
}

func main() {
	flag.Parse()
	interval := time.Duration(int64(checkNewWordInterval) * int64(time.Second))
	ticker := time.NewTicker(interval)
	for {
		select {
		case <-ticker.C:
			if whetherEnableSeekNewWords == 1 {
				autoVocabulary.AutomateUpdateVocabularyList()
			}
			if whetherEnableAdjustColorFunction == 1 {
				adjustTemperature.AdjustComputerColorTemperature()
			}
		}
	}
}
