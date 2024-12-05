<?php

namespace App\Http\Controllers;

use App\Models\Mahasiswa;
use App\Models\Kelas;
use Illuminate\Http\Request;

class MahasiswaController extends Controller
{
    public function verify(Request $request)
    {
        $photos = $request->input('photos');

        $tempFiles = [];
        foreach ($photos as $index => $photo) {
            $imageData = base64_decode(preg_replace('#^data:image/\w+;base64,#i', '', $photo));
            $filePath = storage_path("app/temp_photo_{$index}.jpg");
            file_put_contents($filePath, $imageData);
            $tempFiles[] = $filePath;
        }

        $pythonScript = base_path('scripts/verify_faces.py');
        $command = escapeshellcmd("python $pythonScript " . implode(' ', $tempFiles));
        $output = shell_exec($command);
        $result = json_decode($output, true);

        foreach ($tempFiles as $file) {
            unlink($file);
        }

        return response()->json($result);
    }


    public function index()
    {
        $mahasiswas = Mahasiswa::with('kelas')->get();
        return view('mahasiswa.index', compact('mahasiswas'));
    }

    public function create()
    {
        $kelas = Kelas::all();
        return view('mahasiswa.create', compact('kelas'));
    }

    public function store(Request $request)
    {
        $request->validate([
            'nim' => 'required|string|max:255|unique:mahasiswas,id',
            'nama' => 'required|string|max:255',
            'kelas_id' => 'required|exists:kelas,id',
            'photos' => 'required|array|min:5',
        ]);

        $mahasiswa = Mahasiswa::create([
            'id' => $request->nim,
            'nama' => $request->nama,
            'kelas_id' => $request->kelas_id,
        ]);

        $folderPath = base_path("scripts/Images/{$mahasiswa->id}");
        if (!file_exists($folderPath)) {
            mkdir($folderPath, 0755, true);
        }

        foreach ($request->photos as $index => $photo) {
            $imageData = base64_decode(preg_replace('#^data:image/\w+;base64,#i', '', $photo));
            $filePath = $folderPath . "/{$index}.jpg";
            file_put_contents($filePath, $imageData);
        }


        return redirect()->route('mahasiswa.index')->with('success', 'Mahasiswa berhasil ditambahkan');
    }

    public function edit($id)
    {
        $mahasiswa = Mahasiswa::findOrFail($id);
        $kelas = Kelas::all(); // Ambil semua kelas

        return view('mahasiswa.edit', compact('mahasiswa', 'kelas'));
    }

    public function update(Request $request, $id)
    {
        $request->validate([
            'nama' => 'required|string|max:255',
            'kelas_id' => 'required|exists:kelas,id',
        ]);


        $mahasiswa = Mahasiswa::findOrFail($id);
        $mahasiswa->update([
            'id' => $request->nim,
            'nama' => $request->nama,
            'kelas_id' => $request->kelas_id,
        ]);

        return redirect()->route('mahasiswa.index')->with('success', 'Mahasiswa berhasil diedit');
    }

    public function destroy($id)
    {
        $mahasiswa = Mahasiswa::findOrFail($id);
        $mahasiswa->delete();

        return redirect()->route('mahasiswa.index')->with('success', 'Mahasiswa berhasil dihapus');
    }
}
