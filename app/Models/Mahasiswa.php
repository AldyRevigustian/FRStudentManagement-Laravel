<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Mahasiswa extends Model
{
    use HasFactory;

    protected $fillable = [
        'id',
        'nama',
        'kelas_id',
        'is_trained'
    ];
    public function kelas()
    {
        return $this->belongsTo(Kelas::class);
    }

    public function absensies()
    {
        return $this->hasMany(Absensi::class);
    }
}
