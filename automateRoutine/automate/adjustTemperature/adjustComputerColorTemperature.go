package adjustTemperature

import (
	"bytes"
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"time"
)

const (
	//The hourth of a day.
	convertMorningTime int = 7
	convertNightTime   int = 17

	modeTimezone  int = 1 //indicate xflux to run with American time zone
	modeLongitude int = 2 //indicate xflux to run with 140 degree longitude
)

const (
	INVALID_PID  int = -1
	INVALID_MODE int = -1
)

func AdjustComputerColorTemperature() {
	runXflux()
}

func isXfluxRunning() bool {
	isRunning := false
	pid, _ := getXfluxPidAndRunMode()
	if pid != INVALID_PID {
		isRunning = true
	}
	return isRunning
}

func getPsgResult() string {
	var (
		out bytes.Buffer
	)
	psCmd := exec.Command("ps", "-elf")
	grepCmd := exec.Command("grep", "xflux")

	grepCmd.Stdin, _ = psCmd.StdoutPipe()
	grepCmd.Stdout = os.Stdout
	grepCmd.Stdout = &out
	_ = grepCmd.Start()
	_ = psCmd.Run()
	_ = grepCmd.Wait()

	return out.String()
}

//a little rough, but work good
func runXflux() {
	currHour := time.Now().Hour()
	isRunning := isXfluxRunning()
	pid, mode := getXfluxPidAndRunMode()
	//fmt.Printf("currHour = %v, isRunning = %v, mode = %v\n", currHour, isRunning, mode)

	if currHour < convertMorningTime && isRunning {
		if mode == modeLongitude {
			return
		}
		killOldXflux(pid)
		xfluxRunMode(modeLongitude)
		return
	}
	if currHour < convertMorningTime && !isRunning {
		xfluxRunMode(modeTimezone)
		return
	}
	if currHour >= convertMorningTime && currHour < convertNightTime && isRunning {
		if mode == modeTimezone {
			return
		}
		killOldXflux(pid)
		xfluxRunMode(modeTimezone)
		return

	}
	if currHour >= convertMorningTime && currHour < convertNightTime && !isRunning {
		xfluxRunMode(modeTimezone)
		return
	}
	if currHour >= convertNightTime && isRunning {
		if mode == modeLongitude {
			return
		}
		killOldXflux(pid)
		xfluxRunMode(modeLongitude)
		return
	}
	if currHour >= convertNightTime && !isRunning {
		xfluxRunMode(modeLongitude)
		return
	}
}

func getXfluxPidAndRunMode() (pid int, mode int) {
	var (
		out       bytes.Buffer
		psgResult string = getPsgResult()
		subStr1   string = "140"
		subStr2   string = "8808"
	)
	if strings.Contains(psgResult, subStr1) {
		mode = modeLongitude
	}
	if strings.Contains(psgResult, subStr2) {
		mode = modeTimezone
	}

	pgrepCmd := exec.Command("pgrep", "xflux")
	pgrepCmd.Stdout = &out
	pgrepCmd.Run() //commad pgrep may return nil, and err is not nil. While this is normal, so we donot need to judge the returned value of function Run().
	if out.String() == "" {
		pid = INVALID_PID
		mode = INVALID_MODE
		return
	}
	trimedPid := strings.TrimSuffix(out.String(), "\n")
	pid, err := strconv.Atoi(trimedPid)
	if err != nil {
		log.Fatal(err)
	}
	return
}

func killOldXflux(pid int) {
	strPid := strconv.Itoa(pid)
	killCmd := exec.Command("kill", "-9", strPid)

	err := killCmd.Run()
	if err != nil {
		log.Fatal(err)
	}
}

func xfluxRunMode(mode int) {
	xfluxCmd := new(exec.Cmd)
	args1 := []string{"-z", "8808", "-k", "4100"}
	args2 := []string{"-g", "140", "-k", "4100"}

	if mode == 1 {
		xfluxCmd = exec.Command("xflux", args1...)
	} else {
		xfluxCmd = exec.Command("xflux", args2...)
	}
	err := xfluxCmd.Run()
	if err != nil {
		log.Fatal(err)
	}
}
