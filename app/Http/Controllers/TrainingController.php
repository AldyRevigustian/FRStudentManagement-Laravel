<?php

namespace App\Http\Controllers;
use App\Models\Mahasiswa;

class TrainingController extends Controller
{
    public function index()
    {
        $mahasiswas = Mahasiswa::with('kelas')->get();
        return view('training.index', compact('mahasiswas'));
    }

    public function store()
    {
        $pythonScript1 = base_path('scripts/augmentasi.py');
        $pythonScript2 = base_path('scripts/train.py');

        $command1 = "python $pythonScript1";
        $command2 = "python $pythonScript2";

        exec($command1, $output1, $status1);
        exec($command2, $output2, $status2);

        if ($status1 === 0 && $status2 === 0) {
            Mahasiswa::query()->update(['is_trained' => 1]);
            return redirect()->route('training.index')->with('success', 'Training Mahasiswa berhasil ');
        } else {
            return redirect()->route('training.index')->with('error', 'Terjadi kesalahan saat Training');
        }
    }
}
