<template>
  <v-sheet class="border-md rounded-lg">
    <h4 class="text-h5 font-weight-bold mb-4 bg-surface-light px-4 py-2">
      Bürgerbüro {{ officeLabel }}
    </h4>

    <Line
      :data="chartData"
      :options="chartOptions"
      class="w-full h-64 px-md-4"
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
import { useDisplay } from "vuetify";
import { getWaitingTimes } from "@/ts/api";
import type { Office, StatusRecord, Statuses } from "@/ts/interfaces";
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
import zoomPlugin from "chartjs-plugin-zoom";
import { toIsoDate } from "@/ts/utils";
import "chartjs-adapter-dayjs-4/dist/chartjs-adapter-dayjs-4.esm";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";

dayjs.extend(utc);
const { mobile } = useDisplay();

Chart.register(
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Tooltip,
  CategoryScale,
  zoomPlugin
);

Chart.defaults.color = "#FFF";
Chart.defaults.font.size = 16;

const props = defineProps<{
  office: Office;
  selectedDate: Date;
  statuses: Statuses;
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

const gridOptions = ref({
  display: true,
  color: "rgba(255, 255, 255, 0.2)",
});

const chartOptions = ref<ChartOptions<"line">>({
  responsive: true,
  animation: false,
  borderColor: "#FFF",
  plugins: {
    tooltip: {
      callbacks: {
        label: function (context) {
          const statusLabel =
            props.statuses[context.parsed.y] || context.parsed.y;
          return `Wartezeit: ${statusLabel}`;
        },
      },
    },
    zoom: {
      pan: {
        enabled: true,
        mode: "x",
      },
      zoom: {
        wheel: {
          enabled: true,
          modifierKey: "ctrl",
        },
        pinch: {
          enabled: true,
        },
        mode: "x",
      },
    },
  },
  scales: {
    x: {
      type: "time",
      time: {
        tooltipFormat: "HH:mm",
        unit: "minute",
        round: "minute",
        displayFormats: {
          minute: "HH:mm",
        },
      },
      ticks: {
        source: "auto",
        callback: function (value: any) {
          const date = new Date(value);
          const minutes = date.getMinutes();
          // Only show ticks at 00, 15, 30, 45 minutes
          if (minutes % 15 === 0) {
            return date.toLocaleTimeString("de-DE", {
              hour: "2-digit",
              minute: "2-digit",
              hour12: false,
            });
          }
          return null;
        },
      },
      title: {
        display: !mobile.value,
        text: "Uhrzeit",
      },
      grid: gridOptions.value,
    },
    y: {
      title: {
        display: !mobile.value,
        text: "Wartezeit",
      },
      grid: gridOptions.value,
      min: 0,
      max: Object.keys(props.statuses).length - 1,
      ticks: {
        stepSize: 1,
        includeBounds: true,
        callback: function (value: any) {
          return props.statuses[value] || "";
        },
      },
    },
  },
});

const chartData = computed<ChartData<"line">>(() => ({
  datasets: [
    {
      label: "Wartezeit",
      data: waitingTime.value.map((record) => ({
        x: (dayjs.utc(record.captured_at) as Dayjs).valueOf(),
        y: record.status_id,
      })),
      borderColor: "rgba(75, 192, 192, 1)",
      backgroundColor: "rgba(75, 192, 192, 0.2)",
      pointStyle: false,
      stepped: "before",
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
