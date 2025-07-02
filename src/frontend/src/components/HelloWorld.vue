<template>
  <v-layout>
    <v-app-bar
      title="Wartezeiten in stuttgarter Bürgerbüros"
      class="position-fixed"
    ></v-app-bar>

    <!-- Desktop: Navigation drawer -->
    <v-navigation-drawer width="330" class="d-none d-md-flex position-fixed">
      <DatePicker v-model="selectedDate" />
    </v-navigation-drawer>

    <v-main>
      <v-container class="fill-height pt-0">
        <!-- Mobile: Date picker above charts -->
        <v-row class="d-flex d-md-none mb-4">
          <v-col cols="12">
            <v-card>
              <v-card-title class="text-h6">Select Date</v-card-title>
              <v-card-text>
                <DatePicker v-model="selectedDate" width="100%" hide-header />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Charts -->
        <v-row>
          <v-col v-for="office in offices" :key="office.id" cols="12" md="6">
            <WaitingTimeChart
              :office="office"
              :selected-date="selectedDate.toDate()"
              :statuses="statuses"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { Office, Statuses } from "@/ts/interfaces";
import { getOffices, getStatuses } from "@/ts/api";
import WaitingTimeChart from "./WaitingTimeChart.vue";
import DatePicker from "./DatePicker.vue";
import dayjs from "dayjs";

const selectedDate = ref(dayjs());
const statuses = ref<Statuses>({});
const offices = ref<Office[]>([]);

onMounted(async () => {
  statuses.value = await getStatuses();
  offices.value = await getOffices();
});
</script>
