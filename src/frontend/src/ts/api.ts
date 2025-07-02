import type { Office, StatusRecord, Statuses } from "./interfaces";
import { toIsoDate } from "./utils";

const BASE_URL = "https://st-wait-api.codingmarco.de";

async function fetchJsonFromApi<T>(path: string): Promise<T> {
  const url = new URL(path, BASE_URL);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function getOffices(): Promise<Office[]> {
  return fetchJsonFromApi<Office[]>("/offices");
}

export async function getWaitingTimes(officeId: number, date: Date | string) {
  const dateString = date instanceof Date ? toIsoDate(date) : date;
  return fetchJsonFromApi<StatusRecord[]>(
    `waiting_times/${officeId}/${dateString}`
  );
}

export async function getStatuses(): Promise<Statuses> {
  return fetchJsonFromApi<Statuses>("/statuses");
}
