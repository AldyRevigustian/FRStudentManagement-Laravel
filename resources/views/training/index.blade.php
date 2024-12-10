<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
            {{ __('Daftar Train') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900 dark:text-gray-100">
                    <form action="{{ route('training.store') }}" method="POST" style="display:inline;">
                        @csrf
                        <button type="submit"
                            class="inline-flex items-center px-4 py-2 bg-gray-200 hover:bg-gray-300 text-black text-sm font-semibold rounded-md focus:outline-none mb-4">
                            Train Mahasiswa
                        </button>
                    </form>

                    @if (session('success'))
                        <div class="mb-4 p-4 bg-green-100 text-green-700 border border-green-300 rounded-lg">
                            <strong class="font-medium">Success!</strong> {{ session('success') }}
                        </div>
                    @elseif (session('error'))
                        <div class="mb-4 p-4 bg-red-100 text-red-700 border border-red-300 rounded-lg">
                            <strong class="font-medium">Gagal!</strong> {{ session('error') }}
                        </div>
                    @endif

                    <table id="mahasiswaTable" class="stripe w-full">
                        <thead>
                            <tr>
                                <th class="w-2">NIM</th>
                                <th>Nama</th>
                                <th>Kelas</th>
                                <th class="w-1/6">Is Trained</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach ($mahasiswas as $mahasiswa)
                                <tr>
                                    <td>{{ $mahasiswa->id }}</td>
                                    <td>{{ $mahasiswa->nama }}</td>
                                    <td>{{ $mahasiswa->kelas->nama }}</td>
                                    <td class="flex space-x-2">
                                        @if ($mahasiswa->is_trained == 0)
                                            <span
                                                class="inline-block px-3 py-1 text-sm font-semibold text-white bg-red-600 rounded-full">Not
                                                Trained</span>
                                        @else
                                            <span
                                                class="inline-block px-3 py-1 text-sm font-semibold text-white bg-green-600 rounded-full">Trained</span>
                                        @endif
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    @push('scripts')
        <script>
            $(document).ready(function() {
                $('#mahasiswaTable').DataTable({
                    "processing": true,
                    "serverSide": false,
                    "paging": true,
                    "searching": true,
                    "ordering": true
                });
            });
        </script>
    @endpush
</x-app-layout>
