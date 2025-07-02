import dayjs from "dayjs";

export function toIsoDate(date: Date): string {
  return dayjs(date).format("YYYY-MM-DD");
}
