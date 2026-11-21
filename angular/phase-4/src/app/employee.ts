export interface Employee {
  id: number;
  code: string; // employee code, e.g. E0001 (社員番号)
  nameJp: string;
  nameEn: string;
  department: string;
  salary: number;
}

export const DEPARTMENTS = ['Sales', 'Engineering', 'HR', 'Finance'];

// Sample data: 25 rows so that paging is visible.
const NAMES: [string, string][] = [
  ['山田 太郎', 'Taro Yamada'], ['鈴木 花子', 'Hanako Suzuki'], ['田中 一郎', 'Ichiro Tanaka'],
  ['佐藤 由紀', 'Yuki Sato'], ['高橋 健', 'Ken Takahashi'], ['伊藤 美咲', 'Misaki Ito'],
  ['渡辺 大輔', 'Daisuke Watanabe'], ['中村 愛', 'Ai Nakamura'], ['小林 翔', 'Sho Kobayashi'],
  ['加藤 結衣', 'Yui Kato'],
];

export const EMPLOYEES: Employee[] = Array.from({ length: 25 }, (_, i) => {
  const [nameJp, nameEn] = NAMES[i % NAMES.length];
  return {
    id: i + 1,
    code: `E${String(i + 1).padStart(4, '0')}`,
    nameJp,
    nameEn,
    department: DEPARTMENTS[i % DEPARTMENTS.length],
    salary: 300000 + (i % 7) * 50000,
  };
});
