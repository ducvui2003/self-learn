export interface Employee {
  id: number;
  nameJp: string;
  nameEn: string;
  department: string;
  salary: number; // yen per month
  notes: string;
}

export const DEPARTMENTS = ['Sales', 'Engineering', 'HR'];

export const EMPLOYEES: Employee[] = [
  { id: 1, nameJp: '山田 太郎', nameEn: 'Taro Yamada', department: 'Sales', salary: 450000, notes: 'Top sales in the Kanto region last year.' },
  { id: 2, nameJp: '鈴木 花子', nameEn: 'Hanako Suzuki', department: 'Engineering', salary: 520000, notes: 'Frontend lead. Works with Angular and React.' },
  { id: 3, nameJp: '田中 一郎', nameEn: 'Ichiro Tanaka', department: 'Engineering', salary: 615000, notes: 'Backend lead. Java and Spring.' },
  { id: 4, nameJp: '佐藤 由紀', nameEn: 'Yuki Sato', department: 'HR', salary: 400000, notes: 'Manages hiring.' },
];
