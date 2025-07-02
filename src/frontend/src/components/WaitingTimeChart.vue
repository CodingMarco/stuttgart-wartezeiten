<template>
  <v-sheet class="border-md rounded-lg">
    <h4 class="text-h5 font-weight-bold mb-4 bg-surface-light px-4 py-2">
      Bürgerbüro {{ officeLabel }}
    </h4>

    <Line
      :data="chartData"
      :options="chartOptions"
      class="w-full h-64 px-4"
      :key="selectedIsoDate"
      v-if="dataAvailable"
    />
    <v-alert
      v-else
      type="info"
      class="mt-4"
      :text="`No waiting times available for ${officeLabel} on ${selectedIsoDate}`"
    />
  </v-sheet>
</template>

<script lang="ts" setup>
import { ref, watch, computed } from "vue";
import { useDate } from "vuetify";
import { getWaitingTimes } from "@/ts/api";
import type { Office, StatusRecord } from "@/ts/interfaces";
import { Line } from "vue-chartjs";
import type { ChartOptions, ChartData } from "chart.js";
import {
  Chart,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  CategoryScale,
  Tooltip,
} from "chart.js";
import { toIsoDate } from "@/ts/utils";
import "chartjs-adapter-dayjs-4/dist/chartjs-adapter-dayjs-4.esm";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";

dayjs.extend(utc);
const dateAdapter = useDate();

Chart.register(
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  CategoryScale
);

const props = defineProps<{
  office: Office;
  selectedDate: Date;
}>();

const officeId = computed(() => props.office.id);
const officeLabel = computed(() => props.office.label);
const selectedIsoDate = computed(() => toIsoDate(props.selectedDate));
const dataAvailable = computed(() => {
  return (
    waitingTimesCache.value[selectedIsoDate.value] &&
    waitingTimesCache.value[selectedIsoDate.value].length > 0
  );
});

interface StatusRecordCache {
  // ISO date string as key
  [key: string]: StatusRecord[];
}

const waitingTimesCache = ref<StatusRecordCache>({});
const waitingTime = computed(
  () => waitingTimesCache.value[selectedIsoDate.value] || []
);

const chartOptions = ref<ChartOptions>({
  responsive: true,
  borderColor: "#FFF",
  plugins: {
    legend: {
      display: true,
      position: "top",
    },
  },
  scales: {
    x: {
      type: "time",
      time: {
        tooltipFormat: "hh:mm",
      },
      title: {
        display: true,
        text: "Date",
      },
    },
    y: {
      title: {
        display: true,
        text: "Waiting Time (minutes)",
      },
    },
  },
});

const chartData = computed<ChartData>(() => ({
  labels: [],
  datasets: [
    {
      label: "Waiting Time",
      data: waitingTime.value.map((record) => ({
        x: (dayjs.utc(record.captured_at) as Dayjs).valueOf(),
        y: record.status_id,
      })),
      borderColor: "rgba(75, 192, 192, 1)",
      backgroundColor: "rgba(75, 192, 192, 0.2)",
      pointStyle: false,
    },
  ],
}));

watch(
  () => props.selectedDate,
  async (newDate) => {
    const isoDate = toIsoDate(newDate);
    if (!waitingTimesCache.value[isoDate]) {
      //debugger;
      try {
        const response = await getWaitingTimes(officeId.value, isoDate);
        waitingTimesCache.value[isoDate] = response;
      } catch (error) {
        waitingTimesCache.value[isoDate] = [];
      }
    }
  },
  { immediate: true }
);
</script>
