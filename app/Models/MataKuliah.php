<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MataKuliah extends Model
{
    use HasFactory;

    protected $fillable = [
        'id',
        'nama'
    ];


    public function absensies()
    {
        return $this->hasMany(Absensi::class);
    }
}
