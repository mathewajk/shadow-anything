<template>
    <div class="grid-wrapper">
      <div class="menu-panel">
        <div class="header">
          <h1>shadow anything.</h1>
          <div class="shadow">shadow anything.</div>
        </div>
        <div class="options">
          <h2>Options</h2>
          <div class="option-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="showFormantTrack" checked="checked"/>
              <span class="checkmark"></span>
              <span>Show formant data</span>
            </label>
          </div>
          <div class="option-row">
            <label class="checkbox-label">
              <input type="checkbox" v-model="showSeparate" />
              <span class="checkmark"></span>
              <span>Show reference on separate graph</span>
            </label>
          </div>
        </div>
        <div class="recorders">
          <audio-recorder id="reference" name="Reference Audio" @sendData="sendData" ref="referenceRecorder"/>
          <audio-recorder id="own" name="Your Audio" @sendData="sendData" ref="ownRecorder"/>
        </div>
        <div>
          <button @click="clearRecordings">Clear recordings</button>
        </div>
      </div>
      <div class="chart-grid">
        <div class="pitch-grid">
          <div v-for="chart in pitchCharts" :key="chart.id" class="chart-container">
            <Scatter
              :id="chart.id"
              :options="pitchChartOptions"
              :data="chart.data"
            />
          </div>
        </div>
        <div v-if="showFormantTrack" class="formant-grid">
          <div v-for="chart in formantCharts" :key="chart.id" class="chart-container">
            <Scatter
              :id="chart.id"
              :options="formantChartOptions"
              :data="chart.data"
            />
          </div>
      </div>
    </div>
  </div>
</template>

<script>

import { Scatter } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement } from 'chart.js'
import AudioRecorder from '../components/AudioRecorder.vue';
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement)

import { useChartStore } from '../stores/chart'
import { mapState } from 'pinia'

ChartJS.defaults.font.size = 16;
ChartJS.defaults.color = '#000';

export default {
  data() {
    return {
      audioData: {
        reference: {
          pitchData: [],
          formantData: {
            F1: [],
            F2: [],
          }
        },
        own: {
          pitchData: [],
          formantData: {
            F1: [],
            F2: [],
          }
        }
      },
      showFormantTrack: false,
      showSeparate: false,
    };
  },
  components: {
    Scatter,
    AudioRecorder
  },
  computed: {
    ...mapState(useChartStore, ['pitchChartOptions', 'formantChartOptions']),
    pitchCharts() {
      let charts = []
      if (this.showSeparate) {
        charts.push({
          id: 'reference-pitch-chart',
          data: {datasets: [this.referencePitchChartData]}
        })
        charts.push({
          id: 'own-pitch-chart',
          data: {datasets: [this.ownPitchChartData]}
        })
      } else {
        charts.push({
          id: 'pitch-chart',
          data: {datasets: [this.referencePitchChartData, this.ownPitchChartData]}
        })
      }
      return charts;
    },
    formantCharts() {
      let charts = []
      if (this.showSeparate) {
          charts.push({
            id: 'reference-formant-chart',
            data: {datasets: [this.formantChartData.datasets[0], this.formantChartData.datasets[1]]}
          })
          charts.push({
            id: 'own-formant-chart',
            data: {datasets: [this.formantChartData.datasets[2], this.formantChartData.datasets[3]]}
          })
      } else {
          charts.push({
            id: 'formant-chart',
            data: this.formantChartData
          })
      }
      return charts
    },
    referencePitchChartData() {
      return {
        label: 'Reference',
        fill: false,
        borderColor: '#f93ab7',
        backgroundColor: '#f93ab7',
        data: this.audioData.reference.pitchData.map((value) => ({ x: value[0], y: value[1] })).filter((value) => {
          return value.y != 0;
        })
      }
    },
    ownPitchChartData() {
      return {
        label: 'You',
        fill: false,
        borderColor: '#a0f063',
        backgroundColor: '#a0f063',
        data: this.audioData.own.pitchData.map((value) => ({ x: value[0], y: value[1] })).filter((value) => {
          return value.y != 0;
        })
      }
    },
    formantChartData() {
      let data = {
        datasets: []
      }
      Object.keys(this.audioData.reference.formantData).forEach((formant, index) => {
        let colors = ['#f93ab7', '#c249df']
        data.datasets.push({
          label: `Reference ${formant}`,
          fill: false,
          borderColor: colors[index],
          backgroundColor: colors[index],
          data: this.audioData.reference.formantData[formant].map((value) => ({ x: value[0], y: value[1] }))
        });
      });
      Object.keys(this.audioData.own.formantData).forEach((formant, index) => {
        let colors = ['#a0f063', '#21d8cb']
        data.datasets.push({
          label: `Your Recording ${formant}`,
          fill: false,
          borderColor: colors[index],
          backgroundColor: colors[index],
          data: this.audioData.own.formantData[formant].map((value) => ({ x: value[0], y: value[1] }))
        });
      });
      return data;
    }
  },
  methods: {
    sendData(data, id) {
      let form = new FormData();
      form.append('audio', data, 'data.mp3');
      form.append('title', 'data.mp3');
      fetch('http://127.0.0.1:5000/pitch', {
        method: 'POST',
        body: form
      })
      .then(response => response.json())
      .then(data => {
        this.audioData[id].pitchData = data.pitch_track;
        this.audioData[id].formantData = data.formant_track;
      });
    },
    clearRecordings() {
      this.audioData = {
        reference: {
          pitchData: [],
          formantData: { F1: [], F2: [] }
        },
        own: {
          pitchData: [],
          formantData: { F1: [], F2: [] }
        }
      }
      console.log(this.$refs.referenceRecorder);
      this.$refs.referenceRecorder.clear();
      this.$refs.ownRecorder.clear();
    }
  }
}
</script>

<style >
h1 {
  font-size: 2rem;
  margin-bottom: 3rem;
  position: relative;
}

.header {
  position: relative;
}

.shadow {
  transform: scaleX(-1) rotate(-180deg);
  position: absolute;
  font-size: 2rem;
  top: 2.2rem;
  left: 0;
  opacity: 0.2;
}

h2 {
  position: relative;
  padding: 0;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

h2::before {
  position: absolute;
  left: -1rem;
  top: 4px;
  content: "";
  display: block;
  width: 3px;
  height: 1.5rem;
  background-color: #000;
}
</style>

<style scoped>


button {
  margin: 5px;
}

.header {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.grid-wrapper {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 10px;
  padding: 2em;
}

.menu-panel {
  display: flex;
  flex-direction: column;
  border-right: 1px solid #ccc;
  padding-left: 2rem;
  padding-right: 1rem;
}

label {
  margin-left: 0.5em;
}

.options {
  margin-bottom: 2em;
}

.icon {
  width: 25px;
  height: 25px;
}

a:hover .icon {
  cursor: pointer;
}

.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.chart-container {
  display: flex;
  width: 100%;
  max-height: 400px;
  min-height: 300px;
  position: relative;
}

.chart-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

/* .pitch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr) );
  gap: 20px;
} */

.formant-grid, .pitch-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

button {
  padding: 0.9rem;
  font-size: 0.9rem;
  font-weight: bold;
  border-radius: 50px;
  border: 3px solid #000;
  background-color: #fff;
  transition: all 0.2s ease-in;
}

button:hover {
  background-color: #000;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease-in;
}

.option-row {
  margin-bottom: 0.5rem;
}

input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  position: relative;
  padding-left: 2rem;
  cursor: pointer;
  transition: all 0.3s ease-out;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 23px;
  width: 23px;
  border: 3px solid #000;
  border-radius: 20px;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-label .checkmark:after {
  left: 6px;
  top: 3px;
  width: 5px;
  height: 10px;
  border: solid #000;
  border-width: 0 3px 3px 0;
  -webkit-transform: rotate(45deg);
  -ms-transform: rotate(45deg);
  transform: rotate(45deg);
}

.checkbox-label input:checked ~ .checkmark:after {
  display: block;
}

/* .checkbox-label input:checked ~ .checkmark {
  background-color: #000;
} */

.checkbox-label input:hover ~ .checkmark {
  background-color: #000;
  transition: all 0.1s ease-in;
}

.checkbox-label input:hover ~ .checkmark:after {
  border: solid #fff;
  border-width: 0 3px 3px 0;
  transition: all 0.1s ease-in;
}

</style>