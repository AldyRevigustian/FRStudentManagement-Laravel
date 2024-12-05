<?php

use App\Http\Controllers\AbsensiController;
use App\Http\Controllers\KelasController;
use App\Http\Controllers\MahasiswaController;
use App\Http\Controllers\MataKuliahController;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\TrainingController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/dashboard', function () {
    return view('dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');

    Route::resource('mahasiswa', MahasiswaController::class);
    Route::resource('training', TrainingController::class);
    Route::post('/mahasiswa/verify', [MahasiswaController::class, 'verify'])->name('mahasiswa.verify');
    Route::resource('kelas', KelasController::class);
    Route::resource('matakuliah', MataKuliahController::class);
    Route::resource('absensi', AbsensiController::class);
});

require __DIR__ . '/auth.php';
