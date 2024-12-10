<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use App\Models\Absensi;
use App\Models\Kelas;
use App\Models\Mahasiswa;
use App\Models\MataKuliah;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        \App\Models\User::factory()->create([
            'name' => 'Test User',
            'email' => 'aldybudiasih@gmail.com',
            'password' => "Akunbaru123*"
        ]);

        Kelas::create(['nama' => 'LG01', 'id' => '1']);
        Kelas::create(['nama' => 'LD01', 'id' => '2']);
        Kelas::create(['nama' => 'LB01', 'id' => '3']);

        MataKuliah::create(['nama' => 'Artificial Intelligence']);
        MataKuliah::create(['nama' => 'Database Technology']);
        MataKuliah::create(['nama' => 'Object Oriented Programming']);

        Mahasiswa::create([
            'id' => 2702303716,
            'nama' => 'Chaewon',
            'kelas_id' => 1,
            'is_trained' => 0
        ]);
        Mahasiswa::create([
            'id' => 2702303717,
            'nama' => 'Kaede',
            'kelas_id' => 1,
            'is_trained' => 0
        ]);
        Mahasiswa::create([
            'id' => 2702303718,
            'nama' => 'Shion',
            'kelas_id' => 1,
            'is_trained' => 0
        ]);

        Absensi::create([
            'tanggal' => '2024-12-01 12:30:20 ',
            'kelas_id' => 1,
            'mata_kuliah_id' => 1,
            'mahasiswa_id' => 2702303716
        ]);

        Absensi::create([
            'tanggal' => '2024-12-01 10:20:10',
            'kelas_id' => 1,
            'mata_kuliah_id' => 1,
            'mahasiswa_id' => 2702303717
        ]);

    }
}
