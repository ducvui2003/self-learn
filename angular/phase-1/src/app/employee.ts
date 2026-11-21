// A plain TypeScript interface. Like a PropTypes/TS type in React or Vue.
export interface Employee {
  id: number;
  nameEn: string;
  nameJp: string; // Japanese name (kanji)
  department: string;
  salary: number; // yen per month
  joinedAt: Date;
  active: boolean;
}

export const EMPLOYEES: Employee[] = [
  { id: 1, nameEn: 'Taro Yamada', nameJp: '山田 太郎', department: 'Sales', salary: 450000, joinedAt: new Date('2019-04-01'), active: true },
  { id: 2, nameEn: 'Hanako Suzuki', nameJp: '鈴木 花子', department: 'Engineering', salary: 520000, joinedAt: new Date('2020-10-01'), active: true },
  { id: 3, nameEn: 'Ichiro Tanaka', nameJp: '田中 一郎', department: 'Engineering', salary: 610000, joinedAt: new Date('2017-04-01'), active: false },
  { id: 4, nameEn: 'Yuki Sato', nameJp: '佐藤 由紀', department: 'HR', salary: 400000, joinedAt: new Date('2022-04-01'), active: true },
];
