<?php

namespace App\Http\Controllers;

use App\Models\Absensi;
use App\Models\Kelas;
use App\Models\MataKuliah;
use Illuminate\Http\Request;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

class AbsensiController extends Controller
{
    public function index()
    {
        $absensis = Absensi::with(['mahasiswa', 'kelas', 'mataKuliah'])->get();
        return view('absensi.index', compact('absensis'));
    }

    public function create()
    {
        $kelas = Kelas::all();
        $matakuliah = MataKuliah::all();
        return view('absensi.create', compact('kelas', 'matakuliah'));
    }

    public function store(Request $request)
    {
        $class_id = $request->kelas_id;
        $class_name = Kelas::findOrFail($class_id)->nama;
        $course_id = $request->matakuliah_id;
        $course_name = MataKuliah::findOrFail($course_id)->nama;

        $pythonPath = 'C:/Users/Asus/AppData/Local/Programs/Python/Python310/python.exe';
        $scriptPath = 'D:/Project/StudentManagement/scripts/main.py';

        $command = [
            'C:/Program Files/Git/bin/bash.exe',
            '-c',
            sprintf(
                '%s %s --selected_class_id %d --selected_class_name "%s" --selected_course_id %d --selected_course_name "%s" &',
                $pythonPath,
                $scriptPath,
                $class_id,
                $class_name,
                $course_id,
                $course_name
            )
        ];

        $process = new Process($command);

        try {
            $process->mustRun();
            return redirect()->route('absensi.index')->with('success', 'Mesin Absensi Berhasil Berjalan ');
        } catch (ProcessFailedException $exception) {
            return redirect()->route('absensi.index')->with('error', 'Mesin Absensi Gagal Berjalan ');
        }
    }

    public function destroy($id)
    {
        $absensi = Absensi::findOrFail($id);
        $absensi->delete();

        return redirect()->route('absensi.index')->with('success', 'Absensi berhasil dihapus');
    }
}
